from typing import List
from bitarray import bitarray
import utils
from domain.message.cancelMessage import CancelMessage
from domain.message.pieceMessage import PieceMessage
from domain.message.requestMessage import RequestMessage
from domain.peer import Peer
from domain.piece import Piece
from service.blockRequester import BlockRequester
from service.pieceGenerator import PieceGenerator
from service.sessionMetrics import SessionMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner
from service.torrentSaver import TorrentSaver
from service.torrentUploader import TorrentUploader


class DownloadSession:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner
        self.__pieces: List[Piece] = PieceGenerator(scanner).generatePiecesWithBlocks()
        self.__otherPeers: List[Peer] = []
        self.__torrentSaver: TorrentSaver = TorrentSaver(scanner)
        self.__torrentUploader: TorrentUploader = TorrentUploader(scanner)
        self.__sessionMetrics: SessionMetrics = SessionMetrics(scanner)
        self.__blockRequester: BlockRequester = BlockRequester(self.__pieces)
        self.__isUploadPaused: bool = False

    def setPeerList(self, peerList: List[Peer]) -> None:
        self.__otherPeers.clear()
        self.__otherPeers.extend(peerList)
        self.__blockRequester.setPeerList(peerList)

    def startDownload(self) -> None:
        self.__torrentSaver.start()
        self.__sessionMetrics.start()

    def startJustUpload(self) -> None:
        self.__sessionMetrics.start()
        self.__sessionMetrics.addDownloadedBytes(self.__scanner.getTotalContentSize())

    async def __afterTorrentDownloadFinishes(self) -> None:
        self.__torrentSaver.setDownloadComplete()
        self.__torrentUploader.start()

    """This can be called anytime"""
    async def stop(self) -> None:
        self.__sessionMetrics.stopTimer()
        self.__torrentSaver.stop()
        self.__torrentUploader.stop()
        await self.__cancelAllRequests()

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
                    self.__blockRequester.decreaseRequestedBlockCount()
                    break

    async def __cancelAllRequests(self) -> None:
        for otherPeer in self.__otherPeers:
            for block in otherPeer.blocksRequestedFromPeer:
                await CancelMessage(block.pieceIndex, block.beginOffset, block.length).send(otherPeer)
            otherPeer.blocksRequestedFromPeer.clear()

    async def requestBlocks(self) -> bool:
        isDownloadFinished: bool = await self.__blockRequester.requestBlocks()
        if isDownloadFinished:
            await self.__afterTorrentDownloadFinishes()
        await self.__cancelAllRequests()
        return isDownloadFinished

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
            self.__blockRequester.markPieceAsDownloaded(piece.index)
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
        blockWithoutData = self.__pieces[pieceIndex].getBlockStartingAtOffset(utils.convert4ByteBigEndianToInteger(message.beginOffset))
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
        blockWithoutData = self.__pieces[pieceIndex].getBlockStartingAtOffset(utils.convert4ByteBigEndianToInteger(message.beginOffset))
        if blockWithoutData is None:
            return
        if blockWithoutData in sender.blocksRequestedByPeer:
            sender.blocksRequestedByPeer.remove(blockWithoutData)

    @property
    def sessionMetrics(self) -> SessionMetrics:
        return self.__sessionMetrics

    @property
    def isDownloadPaused(self) -> bool:
        return self.__blockRequester.isDownloadPaused

    @isDownloadPaused.setter
    def isDownloadPaused(self, newValue: bool) -> None:
        self.__blockRequester.isDownloadPaused = newValue

    @property
    def isUploadPaused(self) -> bool:
        return self.__isUploadPaused

    @isUploadPaused.setter
    def isUploadPaused(self, newValue: bool) -> None:
        self.__isUploadPaused = newValue

    @property
    def downloadedPieces(self) -> bitarray:
        return self.__blockRequester.downloadedPieces

    @downloadedPieces.setter
    def downloadedPieces(self, newValue: List[bool]) -> None:
        self.__blockRequester.setDownloadedPieces(newValue)
