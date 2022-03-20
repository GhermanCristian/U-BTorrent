from typing import Final


class HandshakeResponseValidator:
    MINIMUM_HANDSHAKE_RESPONSE_LENGTH: Final[int] = 68
    PROTOCOL_LENGTH_POSITION: Final[int] = 0
    PROTOCOL_STARTING_POSITION: Final[int] = 1
    PROTOCOL_ENDING_POSITION: Final[int] = 20
    INFO_HASH_STARTING_POSITION: Final[int] = 28
    INFO_HASH_ENDING_POSITION: Final[int] = 48

    def __init__(self, infoHash: bytes, currentProtocol: bytes):
        self.__infoHash: bytes = infoHash
        self.__currentProtocol: bytes = currentProtocol
        self.__handshakeResponse: bytes = b""

    def __validHandshakeResponseLength(self) -> bool:
        return len(self.__handshakeResponse) >= self.MINIMUM_HANDSHAKE_RESPONSE_LENGTH

    def __startsWithProtocolLength(self) -> bool:
        return self.__handshakeResponse[self.PROTOCOL_LENGTH_POSITION] == len(self.__currentProtocol)

    def __validProtocol(self) -> bool:
        return self.__handshakeResponse[self.PROTOCOL_STARTING_POSITION: self.PROTOCOL_ENDING_POSITION] == self.__currentProtocol

    def __validInfoHash(self) -> bool:
        return self.__handshakeResponse[self.INFO_HASH_STARTING_POSITION: self.INFO_HASH_ENDING_POSITION] == self.__infoHash

    def validateHandshakeResponse(self, handshakeResponse: bytes) -> bool:
        self.__handshakeResponse = handshakeResponse
        return self.__validHandshakeResponseLength() and self.__startsWithProtocolLength() and\
            self.__validProtocol() and self.__validInfoHash()
