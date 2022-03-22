from typing import Final


class HaveMessage:
    MESSAGE_ID: Final[int] = 4

    def __init__(self, pieceIndex: int):
        # pieceIndex is 0-indexed
        self.__messageID: bytes = chr(self.MESSAGE_ID).encode()
        self.__pieceIndex: bytes = chr(pieceIndex).encode()

    def getMessage(self) -> bytes:
        return self.__messageID + self.__pieceIndex

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    def __eq__(self, otherMessage):
        return isinstance(otherMessage, HaveMessage) and self.getMessage() == otherMessage.getMessage()

    def __hash__(self):
        return hash((self.__messageID, self.__pieceIndex))