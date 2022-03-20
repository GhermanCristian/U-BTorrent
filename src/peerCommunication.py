from asyncio import Task
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

    async def __getHandshakeResponseFromPeer(self, otherPeer: Peer) -> bytes:
        # TODO - find a way to implement timeouts
        try:
            # TODO - several attempts
            reader, writer = await asyncio.open_connection(otherPeer.getIPRepresentedAsString(), otherPeer.port)
        except Exception as e:
            return b""  # an invalid handshake

        writer.write(self.__createHandshakeMessage())
        await writer.drain()
        handshakeResponse: bytes = await reader.read(2048)
        writer.close()
        await writer.wait_closed()

        return handshakeResponse

    async def __connectToPeer(self, otherPeer: Peer) -> None:
        print(otherPeer)
        try:
            handshakeResponse: bytes = await self.__getHandshakeResponseFromPeer(otherPeer)
        except Exception as e:
            return

        if self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse):
            print("OK")
        else:
            print("Invalid handshake response. Aborting")

    async def __connectToPeers(self) -> None:
        connectTasks: List[Task] = []
        for peer in self.__peerList:
            if peer != self.HOST:
                connectTasks.append(asyncio.create_task(self.__connectToPeer(peer)))
        await asyncio.gather(*connectTasks)

    def start(self) -> None:
        print(self.__createHandshakeMessage())
        asyncio.run(self.__connectToPeers())
