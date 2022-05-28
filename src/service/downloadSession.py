import asyncio
from typing import List, Final, Tuple
from bitarray import bitarray
import utils
from domain.block import Block
from domain.message.cancelMessage import CancelMessage
from domain.message.requestMessage import RequestMessage
from domain.peer import Peer
from domain.piece import Piece
from service.pieceGenerator import PieceGenerator
from service.sessionMetrics import SessionMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner
from service.torrentSaver import TorrentSaver


class DownloadSession:
    def __init__(self, scanner: TorrentMetaInfoScanner, otherPeers: List[Peer]):
        self.__scanner: TorrentMetaInfoScanner = scanner
        self.__pieces: List[Piece] = PieceGenerator(scanner).generatePiecesWithBlocks()
        self.__downloadedPieces: bitarray = bitarray()
        self.__downloadedPieces = [piece.isDownloadComplete for piece in self.__pieces]
        self.__otherPeers: List[Peer] = otherPeers
        self.__currentPieceIndex: int = 0
        self.__currentBlockIndex: int = 0
        self.__torrentSaver: TorrentSaver = TorrentSaver(scanner)
        self.__sessionMetrics: SessionMetrics = SessionMetrics(scanner)

    def addCompletedBytes(self, increment: int) -> None:
        self.__sessionMetrics.addCompletedBytes(increment)

    def __isDownloaded(self) -> bool:
        return all(self.__downloadedPieces)

    def __setDownloadCompleteInTorrentSaver(self) -> None:
        self.__torrentSaver.setDownloadComplete()

    """
    Finds a peer which contains the current piece
    @:return The peer which contains the piece, or None if there are no peers who own that piece
    """
    def __getPeerWithCurrentPiece(self) -> Peer | None:
        # Here we can implement some prioritization algorithms based on download speed (distant future tho)
        # At the moment it gets the first available one
        for peer in self.__otherPeers:
            if peer.hasActiveConnection() and not peer.isChokingMe and peer.amInterestedInIt and peer.availablePieces[self.__currentPieceIndex]:
                return peer

    """
    Finds the next available block that can be requested and the peer which owns it
    @:return A tuple of the block and the peer which owns it
    """
    def __determineNextBlockToRequest(self) -> Tuple[Block, Peer] | None:
        while self.__currentPieceIndex < len(self.__pieces):
            piece: Piece = self.__pieces[self.__currentPieceIndex]
            if not piece.isDownloadComplete:
                peerWithCurrentPiece: Peer | None = self.__getPeerWithCurrentPiece()
                if peerWithCurrentPiece is not None:
                    while self.__currentBlockIndex < len(piece.blocks):
                        block: Block = piece.blocks[self.__currentBlockIndex]
                        self.__currentBlockIndex += 1
                        if not block.isComplete and block not in peerWithCurrentPiece.blocksRequestedFromPeer:
                            return block, peerWithCurrentPiece
            self.__currentPieceIndex += 1
            self.__currentBlockIndex = 0
        print("Reached the end without getting a block. Starting again")
        self.__currentPieceIndex, self.__currentBlockIndex = 0, 0

    async def __requestNextBlock(self) -> None:
        BLOCK_INDEX_IN_TUPLE: Final[int] = 0
        PEER_INDEX_IN_TUPLE: Final[int] = 1

        blockAndPeer: Tuple[Block, Peer] | None = self.__determineNextBlockToRequest()
        if blockAndPeer is None:
            return
        block: Block = blockAndPeer[BLOCK_INDEX_IN_TUPLE]
        peer: Peer = blockAndPeer[PEER_INDEX_IN_TUPLE]

        await RequestMessage(block.pieceIndex, block.beginOffset, block.length).send(peer)
        peer.blocksRequestedFromPeer.append(block)
        print(f"Requested - {block}")

    def __afterTorrentDownloadFinishes(self) -> None:
        self.__setDownloadCompleteInTorrentSaver()
        self.__sessionMetrics.stopAllTimers()

    async def requestBlocks(self) -> None:
        INTERVAL_BETWEEN_REQUEST_MESSAGES: Final[float] = 0.015  # seconds => ~66 requests / second => ~1MBps

        while True:
            await asyncio.sleep(INTERVAL_BETWEEN_REQUEST_MESSAGES)
            if self.__isDownloaded():
                self.__afterTorrentDownloadFinishes()
                return
            await self.__requestNextBlock()

    """
    Sends CancelMessages to all peers to which a request has been made for a given block (excluding the peer which answered the request).
    It also removes the block from the list of requested blocks for all peers (including the sender)
    @:param pieceIndex - index of the piece to which the block belongs
    @:param beginOffset - offset of the block inside its piece
    @:param sender - the peer who answered the PieceRequest
    """
    async def cancelRequestsToOtherPeers(self, pieceIndex: int, beginOffset: int, sender: Peer) -> None:
        for otherPeer in self.__otherPeers:
            for blockIndex in range(len(otherPeer.blocksRequestedFromPeer)):
                if otherPeer.blocksRequestedFromPeer[blockIndex].pieceIndex == pieceIndex and otherPeer.blocksRequestedFromPeer[blockIndex].beginOffset == beginOffset:
                    if otherPeer != sender:
                        await CancelMessage(pieceIndex, beginOffset, otherPeer.blocksRequestedFromPeer[blockIndex].length).send(otherPeer)
                        print(f"Canceled - {utils.convertIPFromIntToString(otherPeer.IP)}, index = {pieceIndex}, offset = {beginOffset}")
                    otherPeer.blocksRequestedFromPeer.pop(blockIndex)
                    break

    @property
    def pieces(self) -> List[Piece]:
        return self.__pieces

    def getPieceHash(self, pieceIndex: int) -> bytes:
        return self.__scanner.getPieceHash(pieceIndex)

    def putPieceInWritingQueue(self, piece: Piece) -> None:
        self.__torrentSaver.putPieceInQueue(piece)

    def markPieceAsDownloaded(self, piece: Piece) -> None:
        self.__downloadedPieces[piece.index] = True
