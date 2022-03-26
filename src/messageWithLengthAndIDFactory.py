from typing import Dict, Type
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


class MessageWithLengthAndIDFactory:
    @staticmethod
    def getMessageFromIDAndPayload(messageID: bytes, payload: bytes) -> MessageWithLengthAndID:
        IDToClassDictionary: Dict[int, Type[MessageWithLengthAndID]] = {
            ChokeMessage.MESSAGE_ID: ChokeMessage,
            UnchokeMessage.MESSAGE_ID: UnchokeMessage,
            InterestedMessage.MESSAGE_ID: InterestedMessage,
            NotInterestedMessage.MESSAGE_ID: NotInterestedMessage,
            HaveMessage.MESSAGE_ID: HaveMessage,
            BitfieldMessage.MESSAGE_ID: BitfieldMessage,
            RequestMessage.MESSAGE_ID: RequestMessage,
            PieceMessage.MESSAGE_ID: PieceMessage,
            CancelMessage.MESSAGE_ID: CancelMessage
        }
        messageIDAsInt: int = int.from_bytes(messageID, "big")
        if messageIDAsInt not in IDToClassDictionary.keys():
            raise Exception("MessageID cannot be mapped to any message type")
        message: MessageWithLengthAndID = IDToClassDictionary[messageIDAsInt]()
        message.setMessagePropertiesFromPayload(payload)
        return message
