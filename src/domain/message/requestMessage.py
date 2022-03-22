from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class RequestMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 6
    LENGTH_PREFIX: Final[int] = 13  # messageID = 1B; pieceIndex, beginOffset, pieceLength = 4B each

    def __init__(self, pieceIndex: int, beginOffset: int, pieceLength: int):
        # pieceIndex and beginOffset are 0-indexed
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)
        self.__beginOffset: bytes = utils.convertIntegerTo4ByteBigEndian(beginOffset)
        self.__pieceLength: bytes = utils.convertIntegerTo4ByteBigEndian(pieceLength)

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex + self.__beginOffset + self.__pieceLength

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def pieceLength(self) -> bytes:
        return self.__pieceLength
