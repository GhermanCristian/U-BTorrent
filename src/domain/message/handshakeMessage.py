from typing import Final
import utils
from domain.message.message import Message


class HandshakeMessage(Message):
    CURRENT_PROTOCOL: Final[bytes] = b"BitTorrent protocol"
    CURRENT_PROTOCOL_LENGTH: Final[bytes] = utils.convertIntegerTo1Byte(len(CURRENT_PROTOCOL))
    RESERVED_HANDSHAKE_MESSAGE_BYTES: Final[bytes] = b"00000000"

    def __init__(self, infoHash: bytes, peerID: str):
        self.__infoHash: bytes = infoHash
        self.__peerID: bytes = peerID.encode()

    def getMessageContent(self) -> bytes:
        return self.CURRENT_PROTOCOL_LENGTH + self.CURRENT_PROTOCOL + self.RESERVED_HANDSHAKE_MESSAGE_BYTES + self.__infoHash + self.__peerID
