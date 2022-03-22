from typing import Final


class CancelMessage:
    MESSAGE_ID: Final[int] = 8
    MESSAGE_LENGTH: Final[int] = 13  # messageID = 1B; pieceIndex, beginOffset, pieceLength = 4B each

    def __init__(self, pieceIndex: int, beginOffset: int, pieceLength: int):
        # pieceIndex and beginOffset are 0-indexed
        self.__messageLength: bytes = self.MESSAGE_LENGTH.to_bytes(4, byteorder="big")
        self.__messageID: bytes = chr(self.MESSAGE_ID).encode()
        self.__pieceIndex: bytes = pieceIndex.to_bytes(4, byteorder="big")
        self.__beginOffset: bytes = beginOffset.to_bytes(4, byteorder="big")
        self.__pieceLength: bytes = pieceLength.to_bytes(4, byteorder="big")

    def getMessage(self) -> bytes:
        return self.__messageLength + self.__messageID + self.__pieceIndex + self.__beginOffset + self.__pieceLength

    @property
    def getMessageLength(self) -> bytes:
        return self.__messageLength

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def pieceLength(self) -> bytes:
        return self.__pieceLength

    def __eq__(self, otherMessage):
        return isinstance(otherMessage, CancelMessage) and self.getMessage() == otherMessage.getMessage()

    def __hash__(self):
        return hash(self.getMessage())
