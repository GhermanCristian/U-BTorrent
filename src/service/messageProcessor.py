import utils
from domain.message.bitfieldMessage import BitfieldMessage
from domain.message.cancelMessage import CancelMessage
from domain.message.chokeMessage import ChokeMessage
from domain.message.haveMessage import HaveMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.message.notInterestedMessage import NotInterestedMessage
from domain.message.pieceMessage import PieceMessage
from domain.message.requestMessage import RequestMessage
from domain.message.unchokeMessage import UnchokeMessage
from domain.peer import Peer
from domain.piece import Piece
from service.downloadSession import DownloadSession


class MessageProcessor:
    def __init__(self, otherPeer: Peer):
        self.__otherPeer = otherPeer

    def __bitfieldMessageAction(self, message: BitfieldMessage) -> None:
        # TODO - add validators for all messages
        self.__otherPeer.availablePieces.clear()
        self.__otherPeer.availablePieces.frombytes(message.bitfield)

    def __haveMessageAction(self, message: HaveMessage) -> None:
        self.__otherPeer.availablePieces[utils.convertByteToInteger(message.pieceIndex)] = 1

    def __chokeMessageAction(self) -> None:
        self.__otherPeer.isChokingMe = True

    def __unchokeMessageAction(self) -> None:
        self.__otherPeer.isChokingMe = False

    async def __interestedMessageAction(self, downloadSession: DownloadSession) -> None:
        self.__otherPeer.isInterestedInMe = True
        await BitfieldMessage(downloadSession.downloadedPieces).send(self.__otherPeer)

    def __notInterestedMessageAction(self) -> None:
        self.__otherPeer.isInterestedInMe = False

    async def __pieceMessageAction(self, message: PieceMessage, downloadSession: DownloadSession) -> None:
        pieceIndex: int = utils.convert4ByteBigEndianToInteger(message.pieceIndex)
        if pieceIndex >= len(downloadSession.pieces) or pieceIndex < 0:
            return

        piece: Piece = downloadSession.pieces[pieceIndex]
        if piece.isDownloadComplete:
            return

        await downloadSession.cancelRequestsToOtherPeers(utils.convert4ByteBigEndianToInteger(message.pieceIndex), utils.convert4ByteBigEndianToInteger(message.beginOffset), self.__otherPeer)
        piece.writeDataToBlock(utils.convert4ByteBigEndianToInteger(message.beginOffset), message.block)
        downloadSession.addCompletedBytes(len(message.block))
        if not piece.isDownloadComplete:
            return

        actualPieceHash: bytes = piece.infoHash
        expectedPieceHash: bytes = downloadSession.getPieceHash(pieceIndex)
        if actualPieceHash == expectedPieceHash:
            downloadSession.putPieceInWritingQueue(piece)
            downloadSession.markPieceAsDownloaded(piece)
        else:
            # there's no need to re-request this - the piece will not be marked as complete, so it will be "caught"
            # in the next search loop of the download session
            piece.clear()
        return

    def __requestMessageAction(self) -> None:
        pass

    def __cancelMessageAction(self) -> None:
        pass

    async def processMessage(self, message: MessageWithLengthAndID, downloadSession: DownloadSession) -> None:
        if isinstance(message, BitfieldMessage):
            self.__bitfieldMessageAction(message)
        elif isinstance(message, HaveMessage):
            self.__haveMessageAction(message)
        elif isinstance(message, ChokeMessage):
            self.__chokeMessageAction()
        elif isinstance(message, UnchokeMessage):
            self.__unchokeMessageAction()
        elif isinstance(message, InterestedMessage):
            await self.__interestedMessageAction(downloadSession)
        elif isinstance(message, NotInterestedMessage):
            self.__notInterestedMessageAction()
        elif isinstance(message, PieceMessage):
            await self.__pieceMessageAction(message, downloadSession)
        elif isinstance(message, RequestMessage):
            self.__requestMessageAction()
        elif isinstance(message, CancelMessage):
            self.__cancelMessageAction()
