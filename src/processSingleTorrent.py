import asyncio
from asyncio import StreamReader
from typing import List, Final, Coroutine
import utils
from domain.message.handshakeMessage import HandshakeMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.peer import Peer
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator
from downloadSession import DownloadSession
from messageProcessor import MessageProcessor
from messageWithLengthAndIDFactory import MessageWithLengthAndIDFactory
from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


class ProcessSingleTorrent:
    ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 3
    MESSAGE_ID_LENGTH: Final[int] = 1
    DOWNLOAD_LOCATION: Final[str] = "Resources\\Downloads"

    def __init__(self, torrentFileName: str):
        self.__scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner(torrentFileName, self.DOWNLOAD_LOCATION)
        self.__infoHash: bytes = self.__scanner.infoHash
        
        trackerConnection: TrackerConnection = TrackerConnection()
        trackerConnection.makeTrackerRequest(self.__scanner.announceURL, self.__scanner.infoHash, self.__scanner.getTotalContentSize())
        self.__peerList: List[Peer] = trackerConnection.peerList
        self.__host: Final[Peer] = trackerConnection.host
        
        self.__peerID: str = TrackerConnection.PEER_ID
        self.__handshakeMessage: HandshakeMessage = HandshakeMessage(self.__infoHash, self.__peerID)
        self.__handshakeResponseValidator: HandshakeResponseValidator = HandshakeResponseValidator(self.__infoHash, HandshakeMessage.CURRENT_PROTOCOL)

    """
    Attempts to read byteCount bytes. If too many empty messages are read in a row, the reading is aborted
    @:param reader - where the data is read from
    @:param byteCount - the number of bytes to be read
    @:returns The read data, of length byteCount or less
    """
    @staticmethod
    async def __attemptToReadBytes(reader: StreamReader, byteCount: int) -> bytes:
        payload: bytes = b""
        completedLength: int = 0
        consecutiveEmptyMessages: int = 0
        while completedLength < byteCount and consecutiveEmptyMessages < 3:
            newSequence: bytes = await reader.read(byteCount - completedLength)  # throws exception ?
            payload += newSequence
            completedLength += len(newSequence)
            if len(newSequence) == 0:
                consecutiveEmptyMessages += 1
            else:
                consecutiveEmptyMessages = 0
        if consecutiveEmptyMessages == 3:
            raise ConnectionError("Error when trying to read message")
        return payload

    """
    Attempts to connect to another peer
    @:param otherPeer - the peer we are trying to communicate with
    @:returns True, if the connection was successful, false otherwise
    """
    async def __attemptToConnectToPeer(self, otherPeer: Peer) -> bool:
        for attempt in range(self.ATTEMPTS_TO_CONNECT_TO_PEER):
            try:
                otherPeer.streamReader, otherPeer.streamWriter = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
                await self.__handshakeMessage.send(otherPeer)
                handshakeResponse: bytes = await self.__attemptToReadBytes(otherPeer.streamReader, HandshakeMessage.HANDSHAKE_LENGTH)
                if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
                    return True
            except Exception:
                pass
            await otherPeer.closeConnection()
        return False

    async def __closeAllActiveConnections(self) -> None:
        await asyncio.gather(*[
            peer.closeConnection() for peer in self.__peerList if peer.hasActiveConnection()
        ])

    """
    Reads an entire message from another peer
    @:param otherPeer - the peer we receive the message from
    @:returns True, if the message has been read successfully, false otherwise
    """
    async def __readMessage(self, otherPeer: Peer) -> bool:
        try:
            lengthPrefix: bytes = await self.__attemptToReadBytes(otherPeer.streamReader, 4)
        except ConnectionError as e:
            print(e)
            return False

        if len(lengthPrefix) == 0:
            print(f"nothing was read - {otherPeer.getIPRepresentedAsString()}")
            return True
        if lengthPrefix == utils.convertIntegerTo4ByteBigEndian(0):
            print(f"keep alive message - {otherPeer.getIPRepresentedAsString()}")
            return True

        messageID: bytes = await self.__attemptToReadBytes(otherPeer.streamReader, self.MESSAGE_ID_LENGTH)
        payloadLength: int = utils.convert4ByteBigEndianToInteger(lengthPrefix) - self.MESSAGE_ID_LENGTH
        payload: bytes = await self.__attemptToReadBytes(otherPeer.streamReader, payloadLength)

        if messageID == utils.convertIntegerTo1Byte(20):
            print(f"Extended protocol - ignored for now - {otherPeer.getIPRepresentedAsString()}")
            return True

        try:
            message: MessageWithLengthAndID = MessageWithLengthAndIDFactory.getMessageFromIDAndPayload(messageID, payload)
            MessageProcessor(otherPeer).processMessage(message, self.__downloadSession)
            print(f"{message} - {otherPeer.getIPRepresentedAsString()}")
        except Exception as e:
            print(e)

        return True

    async def __requestNextBlocks(self) -> None:
        while True:  # TODO - add stopping condition
            await asyncio.sleep(0.15)
            await self.__downloadSession.requestNextBlock()

    async def __exchangeMessagesWithPeer(self, otherPeer) -> None:
        if not await self.__attemptToConnectToPeer(otherPeer):
            return

        await InterestedMessage().send(otherPeer)
        otherPeer.amInterestedInIt = True
        while otherPeer.hasActiveConnection():
            if not await self.__readMessage(otherPeer):
                await otherPeer.closeConnection()

    async def __startTorrentDownload(self) -> None:
        try:
            self.__peerList.remove(self.__host)
        except ValueError:
            pass
        if len(self.__peerList) == 0:
            return

        self.__downloadSession: DownloadSession = DownloadSession(self.__scanner, self.__peerList)
        coroutineList: List[Coroutine] = [self.__exchangeMessagesWithPeer(otherPeer) for otherPeer in self.__peerList]
        coroutineList.append(self.__requestNextBlocks())
        await asyncio.gather(*coroutineList)
        await self.__closeAllActiveConnections()

    """
    Wrapper for the method which communicates with the peers
    """
    def start(self) -> None:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # due to issues with closing the event loop in windows
        asyncio.run(self.__startTorrentDownload())
        # TODO - implement some form of signal handling, in order to call cleanup functions when force-closing the program
