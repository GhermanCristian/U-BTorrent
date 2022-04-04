import utils
from domain.message.bitfieldMessage import BitfieldMessage
from domain.message.chokeMessage import ChokeMessage
from domain.message.haveMessage import HaveMessage
from domain.message.interestedMessage import InterestedMessage
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from domain.message.notInterestedMessage import NotInterestedMessage
from domain.message.unchokeMessage import UnchokeMessage
from domain.peer import Peer


class MessageProcessor:
    def __init__(self, otherPeer: Peer):
        self.__otherPeer = otherPeer

    def __bitfieldMessageAction(self, message: BitfieldMessage) -> None:
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

    def processMessage(self, message: MessageWithLengthAndID) -> None:
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
