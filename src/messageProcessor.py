import utils
from domain.message.bitfieldMessage import BitfieldMessage
from domain.message.chokeMessage import ChokeMessage
from domain.message.haveMessage import HaveMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.message.notInterestedMessage import NotInterestedMessage
from domain.message.pieceMessage import PieceMessage
from domain.message.unchokeMessage import UnchokeMessage
from domain.peer import Peer
from domain.piece import Piece
from downloadSession import DownloadSession


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

    def __interestedMessageAction(self) -> None:
        self.__otherPeer.isInterestedInMe = True

    def __notInterestedMessageAction(self) -> None:
        self.__otherPeer.isInterestedInMe = False

    def __pieceMessageAction(self, message: PieceMessage, downloadSession: DownloadSession) -> None:
        pieceIndex: int = utils.convert4ByteBigEndianToInteger(message.pieceIndex)
        if pieceIndex >= len(downloadSession.pieces) or pieceIndex < 0:
            return

        piece: Piece = downloadSession.pieces[pieceIndex]
        piece.writeDataToBlock(utils.convert4ByteBigEndianToInteger(message.beginOffset), message.block)

        if not piece.isComplete:
            return

        actualPieceHash: bytes = piece.infoHash
        expectedPieceHash: bytes = downloadSession.getPieceHash(pieceIndex)
        if actualPieceHash != expectedPieceHash:
            piece.clear()
            return

        # add piece to queue

    def processMessage(self, message: MessageWithLengthAndID, downloadSession: DownloadSession) -> None:
        if isinstance(message, BitfieldMessage):
            self.__bitfieldMessageAction(message)
        elif isinstance(message, HaveMessage):
            self.__haveMessageAction(message)
        elif isinstance(message, ChokeMessage):
            self.__chokeMessageAction()
        elif isinstance(message, UnchokeMessage):
            self.__unchokeMessageAction()
        elif isinstance(message, InterestedMessage):
            self.__interestedMessageAction()
        elif isinstance(message, NotInterestedMessage):
            self.__notInterestedMessageAction()
        elif isinstance(message, PieceMessage):
            self.__pieceMessageAction(message, downloadSession)
