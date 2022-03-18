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
        return self.CURRENT_PROTOCOL_LENGTH + self.CURRENT_PROTOCOL + self.RESERVED_HANDSHAKE_MESSAGE_BYTES +\
            self.__infoHash + self.__peerID.encode()

    def __connectToPeer(self, otherPeer: Peer) -> None:
        print(otherPeer)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(60)
        clientSocket.connect((otherPeer.getIPRepresentedAsString(), otherPeer.port))
        clientSocket.sendall(self.__createHandshakeMessage())
        buffer = clientSocket.recv(2048)
        print("response = " + str(buffer))
        clientSocket.close()

    def start(self):
        print(self.__createHandshakeMessage())
        # for now, just a POC - connecting to one peer, no async yet
        self.__connectToPeer(random.choice(self.__peerList))
        """for peer in self.__peerList:
            if peer != self.HOST:
                print(peer)"""
