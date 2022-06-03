import utils
from domain.message.bitfieldMessage import BitfieldMessage
from domain.message.cancelMessage import CancelMessage
from domain.message.chokeMessage import ChokeMessage
from domain.message.haveMessage import HaveMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.message import Message
from domain.message.notInterestedMessage import NotInterestedMessage
from domain.message.pieceMessage import PieceMessage
from domain.message.requestMessage import RequestMessage
from domain.message.unchokeMessage import UnchokeMessage
from domain.peer import Peer
from domain.piece import Piece
from service.downloadSession import DownloadSession


class MessageProcessor:
    def __init__(self, sender: Peer, downloadSession: DownloadSession):
        self.__sender: Peer = sender
        self.__downloadSession: DownloadSession = downloadSession

    def __bitfieldMessageAction(self, message: BitfieldMessage) -> None:
        # TODO - add validators for all messages
        self.__sender.availablePieces.clear()
        self.__sender.availablePieces.frombytes(message.bitfield)

    def __haveMessageAction(self, message: HaveMessage) -> None:
        self.__sender.availablePieces[utils.convertByteToInteger(message.pieceIndex)] = 1

    def __chokeMessageAction(self) -> None:
        self.__sender.isChokingMe = True

    def __unchokeMessageAction(self) -> None:
        self.__sender.isChokingMe = False

    async def __interestedMessageAction(self) -> None:
        self.__sender.isInterestedInMe = True
        await BitfieldMessage(self.__downloadSession.downloadedPieces).send(self.__sender)

    def __notInterestedMessageAction(self) -> None:
        self.__sender.isInterestedInMe = False

    async def __pieceMessageAction(self, message: PieceMessage) -> None:
        pieceIndex: int = utils.convert4ByteBigEndianToInteger(message.pieceIndex)
        if pieceIndex >= len(self.__downloadSession.pieces) or pieceIndex < 0:
            return

        piece: Piece = self.__downloadSession.pieces[pieceIndex]
        if piece.isDownloadComplete:
            return

        await self.__downloadSession.cancelRequestsToOtherPeers(utils.convert4ByteBigEndianToInteger(message.pieceIndex), utils.convert4ByteBigEndianToInteger(message.beginOffset), self.__sender)
        piece.writeDataToBlock(utils.convert4ByteBigEndianToInteger(message.beginOffset), message.block)
        self.__downloadSession.addCompletedBytes(len(message.block))
        if not piece.isDownloadComplete:
            return

        actualPieceHash: bytes = piece.infoHash
        expectedPieceHash: bytes = self.__downloadSession.getPieceHash(pieceIndex)
        if actualPieceHash == expectedPieceHash:
            self.__downloadSession.putPieceInWritingQueue(piece)
            self.__downloadSession.markPieceAsDownloaded(piece)
        else:
            # there's no need to re-request this - the piece will not be marked as complete, so it will be "caught"
            # in the next search loop of the download session
            piece.clear()
        return

    def __requestMessageAction(self) -> None:
        pass

    def __cancelMessageAction(self) -> None:
        pass

    async def processMessage(self, message: Message) -> None:
        if isinstance(message, BitfieldMessage):
            self.__bitfieldMessageAction(message)
        elif isinstance(message, HaveMessage):
            self.__haveMessageAction(message)
        elif isinstance(message, ChokeMessage):
            self.__chokeMessageAction()
        elif isinstance(message, UnchokeMessage):
            self.__unchokeMessageAction()
        elif isinstance(message, InterestedMessage):
            await self.__interestedMessageAction()
        elif isinstance(message, NotInterestedMessage):
            self.__notInterestedMessageAction()
        elif isinstance(message, PieceMessage):
            await self.__pieceMessageAction(message)
        elif isinstance(message, RequestMessage):
            self.__requestMessageAction()
        elif isinstance(message, CancelMessage):
            self.__cancelMessageAction()
