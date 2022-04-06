import asyncio
from asyncio import StreamReader, StreamWriter
from typing import List, Final, Dict, Tuple
from bitarray import bitarray
import utils
from domain.message.handshakeMessage import HandshakeMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.message import Message
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.message.requestMessage import RequestMessage
from domain.peer import Peer
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator
from messageProcessor import MessageProcessor
from messageWithLengthAndIDFactory import MessageWithLengthAndIDFactory
from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


class ProcessSingleTorrent:
    ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 3
    MESSAGE_ID_LENGTH: Final[int] = 1

    def __init__(self, torrentFileName: str):
        self.__scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner(torrentFileName)
        trackerConnection: TrackerConnection = TrackerConnection()
        trackerConnection.makeTrackerRequest(self.__scanner.getAnnounceURL(), self.__scanner.getInfoHash(), self.__scanner.getTotalContentSize())
        self.__completedPieces: bitarray = bitarray(self.__scanner.getPieceCount())  # this will have to be loaded from disk when resuming downloads
        self.__completedPieces.setall(0)
        self.__initialPeerList: List[Peer] = trackerConnection.peerList
        self.__host: Final[Peer] = trackerConnection.host
        self.__infoHash: bytes = self.__scanner.getInfoHash()
        self.__peerID: str = TrackerConnection.PEER_ID
        self.__handshakeMessage: HandshakeMessage = HandshakeMessage(self.__infoHash, self.__peerID)
        self.__handshakeResponseValidator: HandshakeResponseValidator = HandshakeResponseValidator(self.__infoHash, HandshakeMessage.CURRENT_PROTOCOL)
        self.__activeConnections: Dict[Peer, Tuple[StreamReader, StreamWriter]] = {}

    """
    Closes the connection to a given writer
    @:param readerWriterPair - contains the StreamWriter object to be closed
    """
    async def __closeConnection(self, readerWriterPair: Tuple[StreamReader, StreamWriter]) -> None:
        readerWriterPair[1].close()
        await readerWriterPair[1].wait_closed()

    """
    Attempts to read byteCount bytes. If too many empty messages are read in a row, the reading is aborted
    @:param reader - where the data is read from
    @:param byteCount - the number of bytes to be read
    @:returns The read data, of length byteCount or less
    """
    async def __attemptToReadBytes(self, reader: StreamReader, byteCount: int) -> bytes:
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
        return payload

    """
    Attempts to connect to another peer
    @:param otherPeer - the peer we are trying to communicate with
    @:returns True, if the connection was successful, false otherwise
    """
    async def __attemptToConnectToPeer(self, otherPeer: Peer) -> bool:
        reader, writer = None, None  # cannot really specify types here; the default StreamWriter constructor requires some values
        for attempt in range(self.ATTEMPTS_TO_CONNECT_TO_PEER):
            try:
                reader, writer = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
                await self.__sendMessage(writer, self.__handshakeMessage)
                handshakeResponse: bytes = await self.__attemptToReadBytes(reader, HandshakeMessage.HANDSHAKE_LENGTH)
                if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
                    self.__activeConnections[otherPeer] = (reader, writer)
                    return True
                await self.__closeConnection((reader, writer))
            except Exception:
                if reader is not None and writer is not None:
                    await self.__closeConnection((reader, writer))
        return False

    async def __closeAllConnections(self) -> None:
        await asyncio.gather(*[
            self.__closeConnection(readerWriterPair) for readerWriterPair in self.__activeConnections.values()
        ])

    """
    Sends a message to another peer through a StreamWriter
    @:param writer - data is sent through it
    @:param message - the message to be sent
    """
    async def __sendMessage(self, writer: StreamWriter, message: Message) -> None:
        try:
            writer.write(message.getMessageContent())
            await writer.drain()
        except Exception as e:
            print(e)

    async def __sendRequestMessage(self, otherPeer: Peer, pieceIndex: int, beginOffset: int, pieceLength: int) -> None:
        await self.__sendMessage(self.__activeConnections[otherPeer][1], RequestMessage(pieceIndex, beginOffset, pieceLength))

    async def __requestPiece(self, otherPeer: Peer) -> None:
        pieceIndex: int = 69
        if not otherPeer.isChokingMe and otherPeer.amInterestedInIt and otherPeer.availablePieces[pieceIndex]:
            print(f"making request to {otherPeer.getIPRepresentedAsString()}")
            await self.__sendRequestMessage(otherPeer, pieceIndex, 0, 2 ** 14)

    """
    Reads an entire message from another peer
    @:param otherPeer - the peer we receive the message from
    @:returns True, if the message has been read successfully, false otherwise
    """
    async def __readMessage(self, otherPeer: Peer) -> bool:
        reader: StreamReader = self.__activeConnections[otherPeer][0]
        try:
            lengthPrefix: bytes = await self.__attemptToReadBytes(reader, 4)
        except ConnectionError as e:
            print(e)
            return False

        if len(lengthPrefix) == 0:
            print(f"nothing was read - {otherPeer.getIPRepresentedAsString()}")
            return True
        if lengthPrefix == utils.convertIntegerTo4ByteBigEndian(0):
            print(f"keep alive message - {otherPeer.getIPRepresentedAsString()}")
            return True

        messageID: bytes = await self.__attemptToReadBytes(reader, self.MESSAGE_ID_LENGTH)
        payloadLength: int = utils.convert4ByteBigEndianToInteger(lengthPrefix) - self.MESSAGE_ID_LENGTH
        payload: bytes = await self.__attemptToReadBytes(reader, payloadLength)

        if messageID == utils.convertIntegerTo1Byte(20):
            print(f"Extended protocol - ignored for now - {otherPeer.getIPRepresentedAsString()}")
            return True

        try:
            message: MessageWithLengthAndID = MessageWithLengthAndIDFactory.getMessageFromIDAndPayload(messageID, payload)
            MessageProcessor(otherPeer).processMessage(message)
            print(f"{message} - {otherPeer.getIPRepresentedAsString()}")
        except Exception as e:
            print(e)

        return True

    async def __sendInterestedMessage(self, otherPeer: Peer) -> None:
        await self.__sendMessage(self.__activeConnections[otherPeer][1], InterestedMessage())

    async def __startPeer(self, otherPeer) -> None:
        if not await self.__attemptToConnectToPeer(otherPeer):
            return

        await self.__sendInterestedMessage(otherPeer)
        otherPeer.amInterestedInIt = True
        for _ in range(6):  # will probably become while True
            if not await self.__readMessage(otherPeer):
                return
            await self.__requestPiece(otherPeer)

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
