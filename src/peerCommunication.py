from asyncio import Task, StreamReader, StreamWriter
from typing import List, Final, Dict, Tuple
from domain.message.handshakeMessage import HandshakeMessage
from domain.peer import Peer
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator
import asyncio


class PeerCommunication:
    # TODO - determine IP dynamically; get port from trackerConnection
    HOST_IP: Final[int] = 3155919880  # 188.27.132.8
    HOST: Final[Peer] = Peer(HOST_IP, 6881)
    ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 3
    MAX_HANDSHAKE_RESPONSE_SIZE: Final[int] = 1024

    def __init__(self, peerList: List[Peer], infoHash: bytes, peerID: str):
        self.__initialPeerList: List[Peer] = peerList
        self.__infoHash: bytes = infoHash
        self.__peerID: str = peerID
        self.__handshakeMessage: HandshakeMessage = HandshakeMessage(self.__infoHash, self.__peerID)  # will be specific to each torrent; in the future perhaps have a list
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
                writer.write(self.__handshakeMessage.getMessage())
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

    """
    Attempts to connect to all available peers and exchange handshake messages with them
    """
    async def __connectToPeers(self) -> None:
        connectTasks: List[Task] = []
        for peer in self.__initialPeerList:
            if peer != self.HOST:
                connectTasks.append(asyncio.create_task(self.__attemptToConnectToPeer(peer)))
        await asyncio.gather(*connectTasks)
        await self.__closeAllConnections()

    """
    Wrapper for the method which connects to the peers
    """
    def start(self) -> None:
        asyncio.run(self.__connectToPeers())
