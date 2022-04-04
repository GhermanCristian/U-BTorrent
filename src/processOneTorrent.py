import asyncio
from asyncio import Task, StreamReader, StreamWriter
from typing import List, Final, Dict, Tuple
from bitarray import bitarray
import utils
from domain.message.handshakeMessage import HandshakeMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.peer import Peer
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator
from messageWithLengthAndIDFactory import MessageWithLengthAndIDFactory
from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


class ProcessOneTorrent:
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
    async def __attemptToConnectToPeer(self, otherPeer: Peer) -> None:
        for attempt in range(self.ATTEMPTS_TO_CONNECT_TO_PEER):
            reader, writer = None, None  # cannot really specify types here; the default StreamWriter constructor requires some values
            try:
                reader, writer = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
                writer.write(self.__handshakeMessage.getMessageContent())
                await writer.drain()
                handshakeResponse: bytes = await reader.read(self.MAX_HANDSHAKE_RESPONSE_SIZE)
                if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
                    self.__activeConnections[otherPeer] = (reader, writer)
                    return
                else:
                    await self.__closeConnection((reader, writer))
            except:
                if reader is not None and writer is not None:
                    await self.__closeConnection((reader, writer))

    async def __closeAllConnections(self):
        closeConnectionTasks: List[Task] = []
        for readerWriterPair in self.__activeConnections.values():
            closeConnectionTasks.append(asyncio.create_task(self.__closeConnection(readerWriterPair)))
        await asyncio.gather(*closeConnectionTasks)

    async def __readMessage(self, otherPeer: Peer) -> None:
        reader: StreamReader = self.__activeConnections[otherPeer][0]
        lengthPrefix: bytes = await reader.read(4)
        if len(lengthPrefix) == 0:
            print("nothing was read")
            return

        if lengthPrefix == utils.convertIntegerTo4ByteBigEndian(0):
            print("keep alive message")
            return

        messageID: bytes = await reader.read(1)
        payloadLength: int = int.from_bytes(lengthPrefix, "big") - 1
        payload: bytes = await reader.read(payloadLength)
        if messageID == utils.convertIntegerTo1Byte(20):
            print("Extended protocol - ignored for now")
            return
        message: MessageWithLengthAndID = MessageWithLengthAndIDFactory.getMessageFromIDAndPayload(messageID, payload)
        print(str(message) + " - " + str(otherPeer.IP))

    async def __readMessages(self) -> None:
        readMessageTasks: List[Task] = []
        for otherPeer in self.__activeConnections.keys():
            readMessageTasks.append(asyncio.create_task(self.__readMessage(otherPeer)))
        await asyncio.gather(*readMessageTasks)

    """
    Attempts to connect to all available peers and exchange messages with them
    """
    async def __peerCommunication(self) -> None:
        connectTasks: List[Task] = []
        for peer in self.__initialPeerList:
            if peer != self.__host:
                connectTasks.append(asyncio.create_task(self.__attemptToConnectToPeer(peer)))
        await asyncio.gather(*connectTasks)
        for _ in range(5):  # this will probably turn into a while True
            await self.__readMessages()
        await self.__closeAllConnections()

    """
    Wrapper for the method which communicates with the peers
    """
    def start(self) -> None:
        asyncio.run(self.__peerCommunication())
