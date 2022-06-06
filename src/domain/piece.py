import hashlib
from typing import List
from domain.block import Block


class Piece:
    def __init__(self, index: int, blocks: List[Block]):
        self.__index: int = index
        self.__blocks: List[Block] = blocks

    """
    Clears all the blocks inside the current piece
    """
    def clear(self) -> None:
        [block.clear() for block in self.__blocks]

    def getBlockStartingAtOffset(self, beginOffset: int) -> Block | None:
        blockStartingAtOffset: List[Block] = [block for block in self.__blocks if block.beginOffset == beginOffset]
        if len(blockStartingAtOffset) != 1:
            return None
        return blockStartingAtOffset[0]

    """
    Writes data to a specific block inside the current piece
    @:param beginOffset - the offset of the block we are writing to, zero-indexed
    @:param data - the data that is being written
    """
    def writeDataToBlock(self, beginOffset: int, data: bytes) -> None:
        blockStartingAtOffset: Block | None = self.getBlockStartingAtOffset(beginOffset)
        if blockStartingAtOffset is not None:
            blockStartingAtOffset.writeData(data)

    @property
    def index(self) -> int:
        return self.__index

    @property
    def blocks(self) -> List[Block]:
        return self.__blocks

    @property
    def data(self) -> bytes:
        return b"".join([block.data for block in self.__blocks])

    @property
    def infoHash(self) -> bytes:
        return hashlib.sha1(self.data).digest()

    @property
    def isDownloadComplete(self) -> bool:
        return all([block.isComplete for block in self.__blocks])

    @property
    def isInProgress(self) -> bool:
        isCompleteBlockList: List[bool] = [block.isComplete for block in self.__blocks]
        return any(isCompleteBlockList) and not all(isCompleteBlockList)

    def __str__(self) -> str:
        return f"Piece {self.__index}, containing {len(self.__blocks)} blocks"

    def __eq__(self, other) -> bool:
        return isinstance(other, Piece) and self.__index == other.__index and self.__blocks == other.blocks

    def __hash__(self) -> int:
        return hash((self.__index, self.__blocks))
