from asyncio import Task, StreamReader, StreamWriter
from typing import List, Final
from domain.peer import Peer
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator
import asyncio


class PeerCommunication:
    # TODO - determine IP dynamically; get port from trackerConnection
    HOST_IP: Final[int] = 3155919880  # 188.27.132.8
    HOST: Final[Peer] = Peer(HOST_IP, 6881)
    CURRENT_PROTOCOL: Final[bytes] = b"BitTorrent protocol"
    CURRENT_PROTOCOL_LENGTH: Final[bytes] = chr(len(CURRENT_PROTOCOL)).encode()  # TODO - make this cleaner
    RESERVED_HANDSHAKE_MESSAGE_BYTES: Final[bytes] = b"00000000"
    ATTEMPTS_TO_CONNECT_TO_PEER: Final[int] = 3
    MAX_HANDSHAKE_RESPONSE_SIZE: Final[int] = 1024

    def __init__(self, peerList: List[Peer], infoHash: bytes, peerID: str):
        self.__peerList: List[Peer] = peerList
        self.__infoHash: bytes = infoHash
        self.__peerID: str = peerID
        self.__handshakeResponseValidator: HandshakeResponseValidator = HandshakeResponseValidator(self.__infoHash, self.CURRENT_PROTOCOL)

    """
    Creates a handshake message, according to the current protocol and infoHash
    @:return The handshake message, in bytes form
    """
    def __createHandshakeMessage(self) -> bytes:
        return self.CURRENT_PROTOCOL_LENGTH + self.CURRENT_PROTOCOL + self.RESERVED_HANDSHAKE_MESSAGE_BYTES + \
               self.__infoHash + self.__peerID.encode()

    """
    Sends the handshake to another peer (through a StreamWriter), and receives back a message from it (through a StreamReader)
    @:return The response from the other peer
    """
    async def __exchangeHandshake(self, reader: StreamReader, writer: StreamWriter) -> bytes:
        writer.write(self.__createHandshakeMessage())
        await writer.drain()
        handshakeResponse: bytes = await reader.read(self.MAX_HANDSHAKE_RESPONSE_SIZE)
        writer.close()
        await writer.wait_closed()

        return handshakeResponse

    """
    Tries to connect to another peer in order to exchange handshake messages
    @:param otherPeer - the peer we are trying to communicate with
    """
    async def __attemptToConnectToPeer(self, otherPeer: Peer) -> None:
        for attempt in range(self.ATTEMPTS_TO_CONNECT_TO_PEER):
            try:
                reader, writer = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
                # TODO - store reader + writer from valid connections (whose handshake is valid) in a dict
                handshakeResponse: bytes = await self.__exchangeHandshake(reader, writer)
                if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
                    print(str(otherPeer) + " - OK")
                else:
                    print(str(otherPeer) + " - Invalid handshake response. Aborting") 
            except:
                pass

    """
    Attempts to connect to all available peers and exchange handshake messages with them
    """
    async def __connectToPeers(self) -> None:
        connectTasks: List[Task] = []
        for peer in self.__peerList:
            if peer != self.HOST:
                connectTasks.append(asyncio.create_task(self.__attemptToConnectToPeer(peer)))
        await asyncio.gather(*connectTasks)

    """
    Wrapper for the method which connects to the peers
    """
    def start(self) -> None:
        asyncio.run(self.__connectToPeers())
