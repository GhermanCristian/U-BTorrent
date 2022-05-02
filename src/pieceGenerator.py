import math
from typing import Final, List
from domain.block import Block
from domain.piece import Piece
from torrentMetaInfoScanner import TorrentMetaInfoScanner


class PieceGenerator:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner

    """
    Generates the block list for the specified piece
    @:param pieceIndex - the index of the piece whose blocks are generated
    @:param blocksInPiece - the number of blocks inside the specified piece
    @:param blockLength - the length in bytes of a regular block (i.e. not the last one)
    @:param finalBlockLength - the length in bytes of the last block in the piece
    @:return the list of blocks for the current piece
    """
    @staticmethod
    def __generateBlocksForPiece(pieceIndex: int, blocksInPiece: int, blockLength: int, finalBlockLength: int) -> List[Block]:
        blockList: List[Block] = [Block(pieceIndex, blockIndex * blockLength, blockLength) for blockIndex in range(blocksInPiece - 1)]
        blockList.append(Block(pieceIndex, (blocksInPiece - 1) * blockLength, finalBlockLength))  # last block in the piece
        return blockList

    """
    Generates the pieces (along their respective blocks) for the current torrent file
    @:return the list of pieces
    """
    def generatePiecesWithBlocks(self) -> List[Piece]:
        BLOCK_REQUEST_SIZE: Final[int] = 16384  # 2 ^ 14 bytes

        pieceCount: int = self.__scanner.pieceCount
        pieceLength: int = self.__scanner.regularPieceLength
        finalPieceLength: int = self.__scanner.finalPieceLength

        blockLength: int = BLOCK_REQUEST_SIZE
        blocksInPiece: int = math.ceil(pieceLength / blockLength)
        finalBlockLength: int = pieceLength % blockLength
        if finalBlockLength == 0:
            finalBlockLength = blockLength
        blocksInFinalPiece: int = math.ceil(finalPieceLength / blockLength)
        finalBlockLengthInFinalPiece: int = finalPieceLength % blockLength
        if finalBlockLengthInFinalPiece == 0:
            finalBlockLengthInFinalPiece = finalBlockLength

        pieceList: List[Piece] = [Piece(pieceIndex, self.__generateBlocksForPiece(pieceIndex, blocksInPiece, blockLength, finalBlockLength)) for pieceIndex in range(pieceCount - 1)]
        pieceList.append(Piece(pieceCount - 1, self.__generateBlocksForPiece(pieceCount - 1, blocksInFinalPiece, blockLength, finalBlockLengthInFinalPiece)))

        return pieceList
