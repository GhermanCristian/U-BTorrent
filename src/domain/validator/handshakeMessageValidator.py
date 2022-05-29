from typing import Final
import utils


class HandshakeMessageValidator:
    def __init__(self, infoHash: bytes, currentProtocol: bytes, handshakeMessage: bytes):
        self.__infoHash: bytes = infoHash
        self.__currentProtocol: bytes = currentProtocol
        self.__handshakeMessage: bytes = handshakeMessage

    def __validHandshakeResponseLength(self) -> bool:
        return len(self.__handshakeMessage) >= utils.HANDSHAKE_MESSAGE_LENGTH

    def __startsWithProtocolLength(self) -> bool:
        PROTOCOL_LENGTH_POSITION: Final[int] = 0
        return self.__handshakeMessage[PROTOCOL_LENGTH_POSITION] == len(self.__currentProtocol)

    def __validProtocol(self) -> bool:
        PROTOCOL_STARTING_POSITION: Final[int] = 1
        PROTOCOL_ENDING_POSITION: Final[int] = 20
        return self.__handshakeMessage[PROTOCOL_STARTING_POSITION: PROTOCOL_ENDING_POSITION] == self.__currentProtocol

    def __validInfoHash(self) -> bool:
        INFO_HASH_STARTING_POSITION: Final[int] = 28
        INFO_HASH_ENDING_POSITION: Final[int] = 48
        return self.__handshakeMessage[INFO_HASH_STARTING_POSITION: INFO_HASH_ENDING_POSITION] == self.__infoHash

    def validate(self) -> bool:
        return self.__validHandshakeResponseLength() and self.__startsWithProtocolLength() and\
            self.__validProtocol() and self.__validInfoHash()
