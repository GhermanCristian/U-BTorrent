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

    def __init__(self, peerList: List[Peer], infoHash: bytes, peerID: str):
        self.__peerList: List[Peer] = peerList
        self.__infoHash: bytes = infoHash
        self.__peerID: str = peerID
        self.__handshakeResponseValidator: HandshakeResponseValidator = HandshakeResponseValidator(self.__infoHash, self.CURRENT_PROTOCOL)

    def __createHandshakeMessage(self) -> bytes:
        return self.CURRENT_PROTOCOL_LENGTH + self.CURRENT_PROTOCOL + self.RESERVED_HANDSHAKE_MESSAGE_BYTES + \
               self.__infoHash + self.__peerID.encode()

    async def __sendAndReceiveHandshake(self, reader: StreamReader, writer: StreamWriter) -> bytes:
        writer.write(self.__createHandshakeMessage())
        await writer.drain()
        handshakeResponse: bytes = await reader.read(2048)
        writer.close()
        await writer.wait_closed()

        return handshakeResponse

    async def __getHandshakeResponseFromPeer(self, otherPeer: Peer) -> bytes:
        for attempt in range(3):
            try:
                reader, writer = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
                return await self.__sendAndReceiveHandshake(reader, writer)
            except:
                pass

        return b""  # an invalid handshake

    async def __connectToPeer(self, otherPeer: Peer) -> None:
        handshakeResponse: bytes = await self.__getHandshakeResponseFromPeer(otherPeer)
        if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
            print(str(otherPeer) + " - OK")
        else:
            print(str(otherPeer) + " - Invalid handshake response. Aborting")

    async def __connectToPeers(self) -> None:
        connectTasks: List[Task] = []
        for peer in self.__peerList:
            if peer != self.HOST:
                connectTasks.append(asyncio.create_task(self.__connectToPeer(peer)))
        await asyncio.gather(*connectTasks)

    def start(self) -> None:
        print(self.__createHandshakeMessage())
        asyncio.run(self.__connectToPeers())
