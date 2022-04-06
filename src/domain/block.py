class Block:
    def __init__(self, pieceIndex: int, beginOffset: int, length: int):
        self.__pieceIndex: int = pieceIndex
        self.__beginOffset: int = beginOffset
        self.__length: int = length
        self.__data: bytes = b""
        self.__isComplete: bool = False

    def clear(self) -> None:
        self.__data = None

    def writeData(self, data: bytes) -> None:
        self.__data = data
        if len(data) == self.__length:
            self.__isComplete = True

    @property
    def pieceIndex(self) -> int:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> int:
        return self.__beginOffset

    @property
    def length(self) -> int:
        return self.__length

    @property
    def data(self) -> bytes:
        return self.__data

    @property
    def isComplete(self) -> bool:
        return self.__isComplete

    def __str__(self) -> str:
        return f"Block starting at {self.__beginOffset} of length {self.__length} inside piece {self.__pieceIndex}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Block) and self.__pieceIndex == other.pieceIndex and self.__beginOffset == other.beginOffset \
               and self.__length == other.length and self.__data == other.data

    def __hash__(self) -> int:
        return hash((self.__pieceIndex, self.__beginOffset, self.__length, self.__data))
