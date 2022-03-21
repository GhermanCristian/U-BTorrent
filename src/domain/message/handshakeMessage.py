from typing import Final


class HandshakeMessage:
    CURRENT_PROTOCOL: Final[bytes] = b"BitTorrent protocol"
    CURRENT_PROTOCOL_LENGTH: Final[bytes] = chr(len(CURRENT_PROTOCOL)).encode()  # TODO - make this cleaner
    RESERVED_HANDSHAKE_MESSAGE_BYTES: Final[bytes] = b"00000000"

    def __init__(self, infoHash: bytes, peerID: str):
        self.__infoHash: bytes = infoHash
        self.__peerID: bytes = peerID.encode()

    def getMessage(self) -> bytes:
        return self.CURRENT_PROTOCOL_LENGTH + self.CURRENT_PROTOCOL + self.RESERVED_HANDSHAKE_MESSAGE_BYTES + self.__infoHash + self.__peerID
