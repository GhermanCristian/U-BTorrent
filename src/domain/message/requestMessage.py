from typing import Final


class RequestMessage:
    MESSAGE_ID: Final[int] = 6

    def __init__(self, pieceIndex: int, beginOffset: int, pieceLength: int):
        # pieceIndex and beginOffset are 0-indexed
        self.__messageID: bytes = chr(self.MESSAGE_ID).encode()
        self.__pieceIndex: bytes = chr(pieceIndex).encode()
        self.__beginOffset: bytes = chr(beginOffset).encode()
        self.__pieceLength: bytes = chr(pieceLength).encode()

    def getMessage(self) -> bytes:
        return self.__messageID + self.__pieceIndex + self.__beginOffset + self.__pieceLength

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
        return isinstance(otherMessage, RequestMessage) and self.getMessage() == otherMessage.getMessage()

    def __hash__(self):
        return hash((self.__messageID, self.__pieceIndex, self.__beginOffset, self.__pieceLength))
