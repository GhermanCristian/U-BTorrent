import random
import socket
from typing import List, Final
from domain.peer import Peer


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

    def __createHandshakeMessage(self) -> bytes:
        return self.CURRENT_PROTOCOL_LENGTH + self.CURRENT_PROTOCOL + self.RESERVED_HANDSHAKE_MESSAGE_BYTES + \
               self.__infoHash + self.__peerID.encode()

    def __checkValidHandshakeResponse(self, handshakeResponse: bytes) -> bool:
        # can't use CURRENT_PROTOCOL_LENGTH because it's in byte form (\x13), whereas handshakeResponse[0] is in dec form (19)
        return len(handshakeResponse) >= 68 and handshakeResponse[0] == len(self.CURRENT_PROTOCOL) and \
               handshakeResponse[1:20] == self.CURRENT_PROTOCOL and handshakeResponse[28:48] == self.__infoHash

    def __getHandshakeResponseFromPeer(self, otherPeer: Peer) -> bytes:
        clientSocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(60)
        clientSocket.connect((otherPeer.getIPRepresentedAsString(), otherPeer.port))
        clientSocket.sendall(self.__createHandshakeMessage())
        handshakeResponse: bytes = clientSocket.recv(2048)
        clientSocket.close()
        return handshakeResponse

    def __connectToPeer(self, otherPeer: Peer) -> None:
        print(otherPeer)
        handshakeResponse: bytes = self.__getHandshakeResponseFromPeer(otherPeer)
        print(handshakeResponse)
        assert self.__checkValidHandshakeResponse(handshakeResponse), "Invalid handshake response. Aborting"

    def start(self):
        print(self.__createHandshakeMessage())
        # for now, just a POC - connecting to one peer, no async yet
        self.__connectToPeer(random.choice(self.__peerList))
