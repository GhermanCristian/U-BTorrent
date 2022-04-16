import math
from typing import List, Final, Tuple
from domain.block import Block
from domain.message.requestMessage import RequestMessage
from domain.peer import Peer
from domain.piece import Piece
from torrentMetaInfoScanner import TorrentMetaInfoScanner


class DownloadSession:
    BLOCK_REQUEST_SIZE: Final[int] = 16384  # 2 ^ 14 bytes

    def __init__(self, scanner: TorrentMetaInfoScanner, otherPeers: List[Peer]):
        self.__scanner: TorrentMetaInfoScanner = scanner
        self.__pieces: List[Piece] = self.__generatePiecesWithBlocks()
        self.__otherPeers: List[Peer] = otherPeers
        self.__currentPieceIndex: int = 0
        self.__currentBlockIndex: int = 0

    @staticmethod
    def __generateBlocksForPiece(pieceIndex: int, blocksInPiece: int, blockLength: int, finalBlockLength: int) -> List[Block]:
        blockList: List[Block] = [Block(pieceIndex, blockIndex * blockLength, blockLength) for blockIndex in range(blocksInPiece - 1)]
        blockList.append(Block(pieceIndex, (blocksInPiece - 1) * blockLength, finalBlockLength))  # last block in the piece
        return blockList

    def __generatePiecesWithBlocks(self) -> List[Piece]:
        pieceCount: int = self.__scanner.getPieceCount()
        pieceLength: int = self.__scanner.getPieceLength()
        finalPieceLength: int = self.__scanner.getFinalPieceLength()

        blockLength: int = self.BLOCK_REQUEST_SIZE
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

    def __getPeerWithPiece(self, pieceIndex: int) -> Peer | None:
        # Here we can implement some prioritization algorithms based on download speed (distant future tho)
        # At the moment it gets the first available one
        for peer in self.__otherPeers:
            if peer.hasActiveConnection() and not peer.isChokingMe and peer.amInterestedInIt and peer.availablePieces[pieceIndex]:
                return peer
        return None

    def __determineNextBlockToRequest(self) -> Tuple[Block, Peer] | None:
        while self.__currentPieceIndex < len(self.__pieces):
            piece: Piece = self.__pieces[self.__currentPieceIndex]
            if not piece.isComplete:
                peerWithPiece: Peer | None = self.__getPeerWithPiece(self.__currentPieceIndex)
                if peerWithPiece is not None:
                    while self.__currentBlockIndex < len(piece.blocks):
                        block: Block = piece.blocks[self.__currentBlockIndex]
                        self.__currentBlockIndex += 1
                        if not block.isComplete:
                            return block, peerWithPiece
            self.__currentPieceIndex += 1
            self.__currentBlockIndex = 0
        print("Reached the end without getting a block. Starting again")
        self.__currentPieceIndex, self.__currentBlockIndex = 0, 0

    async def requestBlock(self) -> None:
        blockAndPeer: Tuple[Block, Peer] = self.__determineNextBlockToRequest()
        if blockAndPeer is not None:
            await RequestMessage(blockAndPeer[0].pieceIndex, blockAndPeer[0].beginOffset, blockAndPeer[0].length).send(blockAndPeer[1])
            print(f"Requested - {blockAndPeer[0]}")

    @property
    def pieces(self) -> List[Piece]:
        return self.__pieces

    def getPieceHash(self, pieceIndex: int) -> bytes:
        return self.__scanner.getPieceHash(pieceIndex)
