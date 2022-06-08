import asyncio
from typing import Final, List
from bitarray import bitarray
from domain.block import Block
from domain.message.requestMessage import RequestMessage
from domain.peer import Peer
from domain.piece import Piece


class BlockRequester:
    def __init__(self, pieces: List[Piece]):
        self.__peerList: List[Peer] = []
        self.__pieces: List[Piece] = pieces
        self.__currentPieceIndex: int = 0
        self.__currentBlockIndex: int = 0
        self.__downloadedPieces: bitarray = bitarray()
        self.__requestedBlockCount: int = 0
        self.__isDownloadPaused: bool = False
        
    def setPeerList(self, peerList: List[Peer]) -> None:
        self.__peerList.clear()
        self.__peerList.extend(peerList)

    def decreaseRequestedBlockCount(self) -> None:
        self.__requestedBlockCount -= 1

    def __isDownloaded(self) -> bool:
        return all(self.__downloadedPieces)

    def setDownloadedPieces(self, piecesAlreadyWrittenOnDisk: List[bool]) -> None:
        self.__downloadedPieces.clear()
        self.__downloadedPieces.extend(piecesAlreadyWrittenOnDisk)

    """
    Finds a peer which contains the current piece
    @:return The peer which contains the piece, or None if there are no peers who own that piece
    """
    def __getPeerWithCurrentPiece(self):
        # Here we can implement some prioritization algorithms based on download speed (distant future tho)
        # At the moment it gets the first available one
        for peer in self.__peerList:
            if peer.hasActiveConnection() and not peer.isChokingMe and peer.amInterestedInIt and peer.availablePieces[self.__currentPieceIndex]:
                return peer

    """
    Finds the next available block that can be requested and the peer which owns it
    @:return A tuple of the block and the peer which owns it
    """
    def __determineNextBlockToRequest(self):
        while self.__currentPieceIndex < len(self.__pieces):
            piece: Piece = self.__pieces[self.__currentPieceIndex]
            if not piece.isDownloadComplete:
                peerWithCurrentPiece = self.__getPeerWithCurrentPiece()
                if peerWithCurrentPiece is not None:
                    while self.__currentBlockIndex < len(piece.blocks):
                        block: Block = piece.blocks[self.__currentBlockIndex]
                        self.__currentBlockIndex += 1
                        if not block.isComplete and block not in peerWithCurrentPiece.blocksRequestedFromPeer:
                            return block, peerWithCurrentPiece
            self.__currentPieceIndex += 1
            self.__currentBlockIndex = 0
        self.__currentPieceIndex, self.__currentBlockIndex = 0, 0

    async def __requestNextBlock(self) -> None:
        BLOCK_INDEX_IN_TUPLE: Final[int] = 0
        PEER_INDEX_IN_TUPLE: Final[int] = 1

        blockAndPeer = self.__determineNextBlockToRequest()
        if blockAndPeer is None:
            return
        block: Block = blockAndPeer[BLOCK_INDEX_IN_TUPLE]
        peer: Peer = blockAndPeer[PEER_INDEX_IN_TUPLE]

        await RequestMessage(block.pieceIndex, block.beginOffset, block.length).send(peer)
        peer.blocksRequestedFromPeer.append(block)
        self.__requestedBlockCount += 1

    async def requestBlocks(self) -> bool:
        INTERVAL_BETWEEN_REQUEST_MESSAGES: Final[float] = 0.015  # seconds => ~66 requests / second
        MAX_REQUESTED_BLOCK_COUNT: Final[int] = 2400

        while not self.__isDownloadPaused:
            await asyncio.sleep(INTERVAL_BETWEEN_REQUEST_MESSAGES)
            if self.__isDownloaded():
                return True
            while self.__requestedBlockCount >= MAX_REQUESTED_BLOCK_COUNT:
                await asyncio.sleep(INTERVAL_BETWEEN_REQUEST_MESSAGES)
            await self.__requestNextBlock()
        return False

    @property
    def downloadedPieces(self) -> bitarray:
        return self.__downloadedPieces

    @property
    def isDownloadPaused(self) -> bool:
        return self.__isDownloadPaused

    @isDownloadPaused.setter
    def isDownloadPaused(self, newValue: bool) -> None:
        self.__isDownloadPaused = newValue

    def markPieceAsDownloaded(self, pieceIndex: int) -> None:
        self.__downloadedPieces[pieceIndex] = True
