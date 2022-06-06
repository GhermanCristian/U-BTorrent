import asyncio
from typing import List, Final, Tuple
from bitarray import bitarray
import utils
from domain.block import Block
from domain.message.cancelMessage import CancelMessage
from domain.message.pieceMessage import PieceMessage
from domain.message.requestMessage import RequestMessage
from domain.peer import Peer
from domain.piece import Piece
from service.pieceGenerator import PieceGenerator
from service.sessionMetrics import SessionMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner
from service.torrentSaver import TorrentSaver
from service.torrentUploader import TorrentUploader


class DownloadSession:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner
        self.__pieces: List[Piece] = PieceGenerator(scanner).generatePiecesWithBlocks()
        self.__downloadedPieces: bitarray = bitarray()
        self.__otherPeers: List[Peer] = []
        self.__currentPieceIndex: int = 0
        self.__currentBlockIndex: int = 0
        self.__torrentSaver: TorrentSaver = TorrentSaver(scanner)
        self.__torrentUploader: TorrentUploader = TorrentUploader(scanner)
        self.__sessionMetrics: SessionMetrics = SessionMetrics(scanner)
        self.__isDownloadPaused: bool = False
        self.__isUploadPaused: bool = False
        self.__requestedBlockCount: int = 0

    def setPeerList(self, peerList: List[Peer]) -> None:
        self.__otherPeers.clear()
        self.__otherPeers.extend(peerList)

    def startDownload(self) -> None:
        self.__torrentSaver.start()
        self.__sessionMetrics.start()

    def startJustUpload(self) -> None:
        self.__sessionMetrics.start()
        self.__sessionMetrics.addDownloadedBytes(self.__scanner.getTotalContentSize())

    def setDownloadedPieces(self, piecesAlreadyWrittenOnDisk: List[bool]) -> None:
        self.__downloadedPieces.clear()
        self.__downloadedPieces.extend(piecesAlreadyWrittenOnDisk)

    def __isDownloaded(self) -> bool:
        return all(self.__downloadedPieces)

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
        self.__requestedBlockCount += 1

    async def __afterTorrentDownloadFinishes(self) -> None:
        self.__torrentSaver.setDownloadComplete()
        await self.__cancelAllRequests()
        self.__torrentUploader.start()

    """This can be called anytime"""
    async def stop(self) -> None:
        self.__sessionMetrics.stopTimer()
        self.__torrentSaver.stop()
        self.__torrentUploader.stop()
        await self.__cancelAllRequests()

    async def requestBlocks(self) -> bool:
        INTERVAL_BETWEEN_REQUEST_MESSAGES: Final[float] = 0.015  # seconds => ~66 requests / second
        MAX_REQUESTED_BLOCK_COUNT: Final[int] = 2400

        while not self.__isDownloadPaused:
            await asyncio.sleep(INTERVAL_BETWEEN_REQUEST_MESSAGES)
            if self.__isDownloaded():
                await self.__afterTorrentDownloadFinishes()
                return True
            while self.__requestedBlockCount >= MAX_REQUESTED_BLOCK_COUNT:
                await asyncio.sleep(INTERVAL_BETWEEN_REQUEST_MESSAGES)
            await self.__requestNextBlock()
        await self.__cancelAllRequests()
        return False

    """
    Sends CancelMessages to all peers to which a request has been made for a given block (excluding the peer which answered the request).
    It also removes the block from the list of requested blocks for all peers (including the sender)
    @:param pieceIndex - index of the piece to which the block belongs
    @:param beginOffset - offset of the block inside its piece
    @:param sender - the peer who answered the PieceRequest
    """
    async def __cancelRequestsToOtherPeers(self, pieceIndex: int, beginOffset: int, sender: Peer) -> None:
        for otherPeer in self.__otherPeers:
            for blockIndex in range(len(otherPeer.blocksRequestedFromPeer)):
                if otherPeer.blocksRequestedFromPeer[blockIndex].pieceIndex == pieceIndex and otherPeer.blocksRequestedFromPeer[blockIndex].beginOffset == beginOffset:
                    if otherPeer != sender:
                        await CancelMessage(pieceIndex, beginOffset, otherPeer.blocksRequestedFromPeer[blockIndex].length).send(otherPeer)
                    otherPeer.blocksRequestedFromPeer.pop(blockIndex)
                    self.__requestedBlockCount -= 1
                    break

    async def __cancelAllRequests(self) -> None:
        for otherPeer in self.__otherPeers:
            for block in otherPeer.blocksRequestedFromPeer:
                await CancelMessage(block.pieceIndex, block.beginOffset, block.length).send(otherPeer)
            otherPeer.blocksRequestedFromPeer.clear()
        self.__requestedBlockCount = 0

    async def receivePieceMessage(self, message: PieceMessage, sender: Peer) -> None:
        pieceIndex: int = utils.convert4ByteBigEndianToInteger(message.pieceIndex)
        if pieceIndex >= len(self.__pieces) or pieceIndex < 0:
            return
        piece: Piece = self.__pieces[pieceIndex]
        if piece.isDownloadComplete:
            return
        await self.__cancelRequestsToOtherPeers(utils.convert4ByteBigEndianToInteger(message.pieceIndex), utils.convert4ByteBigEndianToInteger(message.beginOffset), sender)
        piece.writeDataToBlock(utils.convert4ByteBigEndianToInteger(message.beginOffset), message.block)
        self.__sessionMetrics.addDownloadedBytes(len(message.block))
        if not piece.isDownloadComplete:
            return

        actualPieceHash: bytes = piece.infoHash
        expectedPieceHash: bytes = self.__scanner.getPieceHash(pieceIndex)
        if actualPieceHash == expectedPieceHash:
            self.__torrentSaver.putPieceInQueue(piece)
            self.__downloadedPieces[piece.index] = True
        else:
            # there's no need to re-request this - the piece will not be marked as complete, so it will be "caught" in the next search loop of the download session
            piece.clear()
        return

    async def receiveRequestMessage(self, message: RequestMessage, sender: Peer) -> None:
        pieceIndex: int = utils.convert4ByteBigEndianToInteger(message.pieceIndex)
        if pieceIndex >= len(self.__pieces) or pieceIndex < 0:
            return
        blockLength: int = utils.convert4ByteBigEndianToInteger(message.blockLength)
        if blockLength > utils.BLOCK_REQUEST_SIZE:
            return
        blockWithoutData: Block | None = self.__pieces[pieceIndex].getBlockStartingAtOffset(utils.convert4ByteBigEndianToInteger(message.beginOffset))
        if blockWithoutData is None:
            return
        if blockWithoutData not in sender.blocksRequestedByPeer:
            sender.blocksRequestedByPeer.append(blockWithoutData)
            self.__torrentUploader.putBlockInQueue(blockWithoutData, sender)

    async def receiveCancelMessage(self, message: CancelMessage, sender: Peer) -> None:
        pieceIndex: int = utils.convert4ByteBigEndianToInteger(message.pieceIndex)
        if pieceIndex >= len(self.__pieces) or pieceIndex < 0:
            return
        blockLength: int = utils.convert4ByteBigEndianToInteger(message.blockLength)
        if blockLength > utils.BLOCK_REQUEST_SIZE:
            return
        blockWithoutData: Block | None = self.__pieces[pieceIndex].getBlockStartingAtOffset(utils.convert4ByteBigEndianToInteger(message.beginOffset))
        if blockWithoutData is None:
            return
        if blockWithoutData in sender.blocksRequestedByPeer:
            sender.blocksRequestedByPeer.remove(blockWithoutData)

    @property
    def sessionMetrics(self) -> SessionMetrics:
        return self.__sessionMetrics

    @property
    def isDownloadPaused(self) -> bool:
        return self.__isDownloadPaused

    @isDownloadPaused.setter
    def isDownloadPaused(self, newValue: bool) -> None:
        self.__isDownloadPaused = newValue

    @property
    def isUploadPaused(self) -> bool:
        return self.__isUploadPaused

    @isUploadPaused.setter
    def isUploadPaused(self, newValue: bool) -> None:
        self.__isUploadPaused = newValue

    @property
    def downloadedPieces(self) -> bitarray:
        return self.__downloadedPieces
