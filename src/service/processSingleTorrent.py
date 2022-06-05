import asyncio
from asyncio import StreamReader, events, AbstractEventLoop
from typing import List, Final, Coroutine, Tuple
import utils
from domain.message.handshakeMessage import HandshakeMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.keepAliveMessage import KeepAliveMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.message.unchokeMessage import UnchokeMessage
from domain.peer import Peer
from domain.validator.handshakeMessageValidator import HandshakeMessageValidator
from service.downloadSession import DownloadSession
from service.messageQueue import MessageQueue
from service.messageWithLengthAndIDFactory import MessageWithLengthAndIDFactory
from service.sessionMetrics import SessionMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner
from service.trackerConnection import TrackerConnection


class ProcessSingleTorrent:
    def __init__(self, torrentFilePath: str, downloadLocation: str):
        self.__scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner(torrentFilePath, downloadLocation)
        self.__trackerConnection: TrackerConnection = TrackerConnection(self.__scanner)
        self.__downloadSession: DownloadSession = DownloadSession(self.__scanner)
        self.__messageQueue: MessageQueue = MessageQueue(self.__downloadSession)
        self.__peerList: List[Peer] = []
        self.__peerDownloadingCoroutines: List[Coroutine] = []
        # using this instead of the usual asyncio.run(), because of issues when calling create_task from another thread (e.g. from the GUI)
        self.__eventLoop: AbstractEventLoop = asyncio.new_event_loop()

    async def __makeTrackerStartedRequest(self) -> None:
        peerList, port = await self.__trackerConnection.makeTrackerStartedRequest()
        self.__host: Peer = Peer(utils.convertIPFromStringToInt(self.__trackerConnection.currentIP), port)
        await self.__addNewPeers(peerList)

    """
    Attempts to read byteCount bytes. If too many empty messages are read in a row, the reading is aborted
    @:param reader - where the data is read from
    @:param byteCount - the number of bytes to be read
    @:returns The read data, of length byteCount or less
    """
    @staticmethod
    async def __attemptToReadBytes(reader: StreamReader, byteCount: int) -> bytes:
        MAX_CONSECUTIVE_EMPTY_MESSAGES: Final[int] = 3

        payload: bytes = b""
        completedLength: int = 0
        consecutiveEmptyMessages: int = 0
        while completedLength < byteCount and consecutiveEmptyMessages < MAX_CONSECUTIVE_EMPTY_MESSAGES:
            newSequence: bytes = await reader.read(byteCount - completedLength)  # throws exception ?
            payload += newSequence
            completedLength += len(newSequence)
            if not newSequence:
                consecutiveEmptyMessages += 1
            else:
                consecutiveEmptyMessages = 0
        if consecutiveEmptyMessages == MAX_CONSECUTIVE_EMPTY_MESSAGES:
            raise ConnectionError("Error when trying to read message")
        return payload

    """
    Attempts to initiate a connection with another peer by exchanging handshake messages
    @:param otherPeer - the peer we are trying to communicate with
    @:returns True, if the connection was successful, false otherwise
    """
    async def __attemptToHandshakeWithPeer(self, otherPeer: Peer) -> bool:
        ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 2
        OPEN_CONNECTION_TIMEOUT_IN_SECONDS: Final[float] = 2.5

        for _ in range(ATTEMPTS_TO_CONNECT_TO_PEER):
            try:
                otherPeer.streamReader, otherPeer.streamWriter = await asyncio.wait_for(asyncio.open_connection(utils.convertIPFromIntToString(otherPeer.IP), otherPeer.port), timeout=OPEN_CONNECTION_TIMEOUT_IN_SECONDS)
                await HandshakeMessage(self.__scanner.infoHash, utils.PEER_ID).send(otherPeer)
                handshakeResponse: bytes = await self.__attemptToReadBytes(otherPeer.streamReader, utils.HANDSHAKE_MESSAGE_LENGTH)
                if HandshakeMessageValidator(self.__scanner.infoHash, HandshakeMessage.CURRENT_PROTOCOL, handshakeResponse).validate():
                    return True
            except Exception:
                pass
            await otherPeer.closeConnection()
        return False

    async def __closeAllActiveConnections(self) -> None:
        await asyncio.gather(*[peer.closeConnection() for peer in self.__peerList if peer.hasActiveConnection()])

    """
    Reads an entire message from another peer and processes it according to its type
    @:param sender - the peer we receive the message from
    @:returns True, if the message has been read successfully, False otherwise
    """
    async def __readMessage(self, sender: Peer) -> bool:
        LENGTH_PREFIX_LENGTH: Final[int] = 4  # bytes
        EXTENDED_PROTOCOL_MESSAGE_ID: Final[int] = 20

        try:
            lengthPrefix: bytes = await self.__attemptToReadBytes(sender.streamReader, LENGTH_PREFIX_LENGTH)
        except ConnectionError as e:
            print(e)
            return False

        if not lengthPrefix or lengthPrefix == utils.convertIntegerTo4ByteBigEndian(KeepAliveMessage.LENGTH_PREFIX):
            return True
        messageID: bytes = await self.__attemptToReadBytes(sender.streamReader, utils.MESSAGE_ID_LENGTH)
        payloadLength: int = utils.convert4ByteBigEndianToInteger(lengthPrefix) - utils.MESSAGE_ID_LENGTH
        payload: bytes = await self.__attemptToReadBytes(sender.streamReader, payloadLength)
        if messageID == utils.convertIntegerTo1Byte(EXTENDED_PROTOCOL_MESSAGE_ID):
            return True

        try:
            message: MessageWithLengthAndID = MessageWithLengthAndIDFactory.getMessageFromIDAndPayload(messageID, payload)
            self.__messageQueue.putMessageInQueue(message, sender)
        except Exception as e:
            print(e)
        return True

    async def __exchangeMessagesWithPeer(self, otherPeer: Peer) -> None:
        while otherPeer.hasActiveConnection():
            if not await self.__readMessage(otherPeer):
                await otherPeer.closeConnection()

    async def __startConnectionToPeerForDownload(self, otherPeer: Peer) -> None:
        await InterestedMessage().send(otherPeer)
        otherPeer.amInterestedInIt = True
        await self.__exchangeMessagesWithPeer(otherPeer)

    async def __startConnectionToPeerForUpload(self, otherPeer: Peer) -> None:
        await UnchokeMessage().send(otherPeer)
        otherPeer.amChokingIt = False
        await self.__exchangeMessagesWithPeer(otherPeer)

    def __removeDisconnectedPeers(self) -> None:
        connectedPeers: List[Peer] = []
        for peer in self.__peerList:
            if peer.hasActiveConnection():
                connectedPeers.append(peer)
        self.__peerList.clear()
        self.__peerList.extend(connectedPeers)

    async def __addNewPeers(self, newPeers: List[Peer]) -> None:
        try:
            newPeers.remove(self.__host)
        except ValueError:
            pass
        for newPeer in newPeers:
            if newPeer not in self.__peerList:
                if await self.__attemptToHandshakeWithPeer(newPeer):
                    self.__peerList.append(newPeer)

    async def __upload(self) -> None:
        newPeersAndPort: Tuple[List[Peer], int] = await self.__trackerConnection.makeTrackerFinishedRequest()
        if newPeersAndPort[1] != self.__host.port:
            self.__host = Peer(utils.convertIPFromStringToInt(self.__trackerConnection.currentIP), newPeersAndPort[1])
        self.__removeDisconnectedPeers()
        await self.__addNewPeers(newPeersAndPort[0])
        [peerDownloadingCoroutine.close() for peerDownloadingCoroutine in self.__peerDownloadingCoroutines]
        print("started uploading")
        await asyncio.gather(*[self.__startConnectionToPeerForUpload(peer) for peer in self.__peerList])

    async def __download(self) -> None:
        isDownloaded: bool = await self.__downloadSession.requestBlocks()
        if isDownloaded:
            await self.__upload()
        else:
            print("just paused")

    async def __startTorrentDownload(self) -> None:
        await self.__makeTrackerStartedRequest()

        if self.__peerList:
            self.__downloadSession.setPeerList(self.__peerList)
            self.__downloadSession.start()
            self.__messageQueue.start()
            self.__peerDownloadingCoroutines.extend([self.__startConnectionToPeerForDownload(otherPeer) for otherPeer in self.__peerList])
            coroutineList: List[Coroutine] = []
            coroutineList.extend(self.__peerDownloadingCoroutines)
            coroutineList.append(self.__download())
            await asyncio.gather(*coroutineList)
            await self.__closeAllActiveConnections()

    def run(self) -> None:
        events.set_event_loop(self.__eventLoop)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # due to issues with closing the event loop on Windows
        # TODO - implement some form of signal handling, in order to call cleanup functions when force-closing the program
        self.__eventLoop.run_until_complete(self.__startTorrentDownload())

    @property
    def sessionMetrics(self) -> SessionMetrics:
        return self.__downloadSession.sessionMetrics
    
    @property
    def isDownloadPaused(self) -> bool:
        return self.__downloadSession.isDownloadPaused

    @property
    def isUploadPaused(self) -> bool:
        return self.__downloadSession.isUploadPaused

    def pauseDownload(self) -> None:
        self.__downloadSession.isDownloadPaused = True

    def resumeDownload(self) -> None:
        self.__downloadSession.isDownloadPaused = False
        self.__eventLoop.create_task(self.__download())

    def pauseUpload(self) -> None:
        self.__downloadSession.isUploadPaused = True

    def resumeUpload(self) -> None:
        self.__downloadSession.isUploadPaused = False

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__scanner.infoHash == other.__scanner.infoHash

    def __hash__(self) -> int:
        return hash(self.__scanner.infoHash)
