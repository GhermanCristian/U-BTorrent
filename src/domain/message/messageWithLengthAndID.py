from abc import abstractmethod
import utils
from domain.message.message import Message


class MessageWithLengthAndID(Message):
    def __init__(self, lengthPrefix: int, messageID: int):
        self._lengthPrefix: bytes = utils.convertIntegerTo4ByteBigEndian(lengthPrefix)
        self._messageID: bytes = utils.convertIntegerTo1Byte(messageID)

    @abstractmethod
    def getMessageContent(self) -> bytes:
        return self._lengthPrefix + self._messageID

    @property
    def getLengthPrefix(self) -> bytes:
        return self._lengthPrefix

    @property
    def getMessageID(self) -> bytes:
        return self._messageID
