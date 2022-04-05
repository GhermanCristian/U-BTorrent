import asyncio
from asyncio import Task, StreamReader, StreamWriter
from typing import List, Final, Dict, Tuple
from bitarray import bitarray
import utils
from domain.message.handshakeMessage import HandshakeMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.peer import Peer
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator
from messageProcessor import MessageProcessor
from messageWithLengthAndIDFactory import MessageWithLengthAndIDFactory
from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


class ProcessSingleTorrent:
    ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 3
    MAX_HANDSHAKE_RESPONSE_SIZE: Final[int] = 68

    def __init__(self, torrentFileName: str):
        scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner(torrentFileName)
        trackerConnection: TrackerConnection = TrackerConnection()
        trackerConnection.makeTrackerRequest(scanner.getAnnounceURL(), scanner.getInfoHash(), scanner.getTotalContentSize())
        self.__completedPieces: bitarray = bitarray(scanner.getPieceCount())  # this will have to be loaded from disk when resuming downloads
        self.__completedPieces.setall(0)
        self.__initialPeerList: List[Peer] = trackerConnection.peerList
        self.__host: Final[Peer] = trackerConnection.host
        self.__infoHash: bytes = scanner.getInfoHash()
        self.__peerID: str = TrackerConnection.PEER_ID
        self.__handshakeMessage: HandshakeMessage = HandshakeMessage(self.__infoHash, self.__peerID)
        self.__handshakeResponseValidator: HandshakeResponseValidator = HandshakeResponseValidator(self.__infoHash, HandshakeMessage.CURRENT_PROTOCOL)
        self.__activeConnections: Dict[Peer, Tuple[StreamReader, StreamWriter]] = {}

    async def __closeConnection(self, readerWriterPair: Tuple[StreamReader, StreamWriter]) -> None:
        readerWriterPair[1].close()
        await readerWriterPair[1].wait_closed()

    """
    Tries to connect to another peer in order to exchange handshake messages
    @:param otherPeer - the peer we are trying to communicate with
    """
    async def __attemptToConnectToPeer(self, otherPeer: Peer) -> bool:
        for attempt in range(self.ATTEMPTS_TO_CONNECT_TO_PEER):
            reader, writer = None, None  # cannot really specify types here; the default StreamWriter constructor requires some values
            try:
                reader, writer = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
                writer.write(self.__handshakeMessage.getMessageContent())
                await writer.drain()
                handshakeResponse: bytes = await reader.read(self.MAX_HANDSHAKE_RESPONSE_SIZE)
                if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
                    self.__activeConnections[otherPeer] = (reader, writer)
                    return True
                await self.__closeConnection((reader, writer))
            except Exception:
                if reader is not None and writer is not None:
                    await self.__closeConnection((reader, writer))
        return False

    async def __closeAllConnections(self):
        closeConnectionTasks: List[Task] = []
        for readerWriterPair in self.__activeConnections.values():
            closeConnectionTasks.append(asyncio.create_task(self.__closeConnection(readerWriterPair)))
        await asyncio.gather(*closeConnectionTasks)

    async def __readMessage(self, otherPeer: Peer) -> bool:
        reader: StreamReader = self.__activeConnections[otherPeer][0]
        try:
            lengthPrefix: bytes = await reader.read(4)
        except ConnectionError as e:
            print(e)
            return False

        if len(lengthPrefix) == 0:
            print(f"nothing was read - {otherPeer.IP}")
            return True

        if lengthPrefix == utils.convertIntegerTo4ByteBigEndian(0):
            print(f"keep alive message - {otherPeer.IP}")
            return True

        messageID: bytes = await reader.read(1)
        payloadLength: int = int.from_bytes(lengthPrefix, "big") - 1
        # TODO - make this a while True with a buffer, because there are some messages which are send through several reads
        payload: bytes = await reader.read(payloadLength)
        if messageID == utils.convertIntegerTo1Byte(20):
            print(f"Extended protocol - ignored for now - {otherPeer.IP}")
            return True
        message: MessageWithLengthAndID = MessageWithLengthAndIDFactory.getMessageFromIDAndPayload(messageID, payload)
        MessageProcessor(otherPeer).processMessage(message)
        print(f"{message} - {otherPeer.IP}")
        return True

    async def __sendInterestedMessage(self, otherPeer) -> None:
        writer: StreamWriter = self.__activeConnections[otherPeer][1]
        writer.write(InterestedMessage().getMessageContent())
        await writer.drain()

    async def __startPeer(self, otherPeer) -> None:
        if not await self.__attemptToConnectToPeer(otherPeer):
            return

        await self.__sendInterestedMessage(otherPeer)
        otherPeer.amInterestedInIt = True
        for _ in range(6):  # will probably become while True
            if not await self.__readMessage(otherPeer):
                return

    async def __peerCommunication(self) -> None:
        try:
            self.__initialPeerList.remove(self.__host)
        except ValueError:
            pass

        await asyncio.gather(*[
            self.__startPeer(otherPeer)
            for otherPeer in self.__initialPeerList
        ])

    """
    Wrapper for the method which communicates with the peers
    """
    def start(self) -> None:
        asyncio.run(self.__peerCommunication())
