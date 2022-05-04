import asyncio
from asyncio import StreamReader
from typing import List, Final, Coroutine
import utils
from domain.message.handshakeMessage import HandshakeMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.keepAliveMessage import KeepAliveMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.peer import Peer
from domain.validator.handshakeMessageValidator import HandshakeMessageValidator
from service.downloadSession import DownloadSession
from service.messageProcessor import MessageProcessor
from service.messageWithLengthAndIDFactory import MessageWithLengthAndIDFactory
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner
from service.trackerConnection import TrackerConnection


class ProcessSingleTorrent:
    def __init__(self, torrentFileName: str):
        DOWNLOAD_LOCATION: Final[str] = "..\\Resources\\Downloads"

        self.__scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner(torrentFileName, DOWNLOAD_LOCATION)
        self.__handshakeMessage: HandshakeMessage = HandshakeMessage(self.__scanner.infoHash, TrackerConnection.PEER_ID)

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # due to issues with closing the event loop in windows
        asyncio.run(self.__startTorrentDownload())
        # TODO - implement some form of signal handling, in order to call cleanup functions when force-closing the program

    async def __makeTrackerConnection(self) -> None:
        trackerConnection: TrackerConnection = TrackerConnection()
        await trackerConnection.makeTrackerRequest(self.__scanner.announceURL, self.__scanner.infoHash, self.__scanner.getTotalContentSize())
        self.__peerList: List[Peer] = trackerConnection.peerList
        self.__host: Peer = trackerConnection.host

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
        ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 3

        for attempt in range(ATTEMPTS_TO_CONNECT_TO_PEER):
            try:
                otherPeer.streamReader, otherPeer.streamWriter = await asyncio.open_connection(utils.convertIPFromIntToString(otherPeer.IP), otherPeer.port)
                await self.__handshakeMessage.send(otherPeer)
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

        if not lengthPrefix:
            return True
        if lengthPrefix == utils.convertIntegerTo4ByteBigEndian(KeepAliveMessage.LENGTH_PREFIX):
            return True
        messageID: bytes = await self.__attemptToReadBytes(sender.streamReader, utils.MESSAGE_ID_LENGTH)
        payloadLength: int = utils.convert4ByteBigEndianToInteger(lengthPrefix) - utils.MESSAGE_ID_LENGTH
        payload: bytes = await self.__attemptToReadBytes(sender.streamReader, payloadLength)
        if messageID == utils.convertIntegerTo1Byte(EXTENDED_PROTOCOL_MESSAGE_ID):
            return True

        try:
            message: MessageWithLengthAndID = MessageWithLengthAndIDFactory.getMessageFromIDAndPayload(messageID, payload)
            await MessageProcessor(sender).processMessage(message, self.__downloadSession, sender)
        except Exception as e:
            print(e)
        return True

    async def __requestNextBlocks(self) -> None:
        INTERVAL_BETWEEN_REQUEST_MESSAGES: Final[float] = 0.015  # seconds => ~66 requests / second => ~1MBps

        while True:
            await asyncio.sleep(INTERVAL_BETWEEN_REQUEST_MESSAGES)
            if self.__downloadSession.isDownloaded():
                self.__downloadSession.setDownloadCompleteInTorrentSaver()
                return
            await self.__downloadSession.requestNextBlock()

    async def __exchangeMessagesWithPeer(self, otherPeer: Peer) -> None:
        if not await self.__attemptToHandshakeWithPeer(otherPeer):
            return

        await InterestedMessage().send(otherPeer)
        otherPeer.amInterestedInIt = True
        while otherPeer.hasActiveConnection():
            if not await self.__readMessage(otherPeer):
                await otherPeer.closeConnection()

    async def __startTorrentDownload(self) -> None:
        await self.__makeTrackerConnection()

        try:
            self.__peerList.remove(self.__host)
        except ValueError:
            pass
        if not self.__peerList:
            return

        self.__downloadSession: DownloadSession = DownloadSession(self.__scanner, self.__peerList)
        coroutineList: List[Coroutine] = [self.__exchangeMessagesWithPeer(otherPeer) for otherPeer in self.__peerList]
        coroutineList.append(self.__requestNextBlocks())
        await asyncio.gather(*coroutineList)
        await self.__closeAllActiveConnections()
