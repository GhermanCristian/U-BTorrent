from typing import Final


class PieceMessage:
    MESSAGE_ID: Final[int] = 7

    def __init__(self, pieceIndex: int, beginOffset: int, block: bytes):
        # pieceIndex and beginOffset are 0-indexed
        self.__messageID: bytes = chr(self.MESSAGE_ID).encode()
        self.__pieceIndex: bytes = chr(pieceIndex).encode()
        self.__beginOffset: bytes = chr(beginOffset).encode()
        self.__block: bytes = block

    def getMessage(self) -> bytes:
        return self.__messageID + self.__pieceIndex + self.__beginOffset + self.__block

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def block(self) -> bytes:
        return self.__block

    def __eq__(self, otherMessage):
        return isinstance(otherMessage, PieceMessage) and self.getMessage() == otherMessage.getMessage()

    def __hash__(self):
        return hash((self.__messageID, self.__pieceIndex, self.__beginOffset, self.__block))
