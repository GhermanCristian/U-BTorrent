from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class PieceMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 7
    BASE_LENGTH_PREFIX: Final[int] = 9  # messageID = 1B; pieceIndex, beginOffset = 4B each

    def __init__(self, pieceIndex: int, beginOffset: int, block: bytes):
        # pieceIndex and beginOffset are 0-indexed
        super().__init__(self.BASE_LENGTH_PREFIX + len(block), self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)
        self.__beginOffset: bytes = utils.convertIntegerTo4ByteBigEndian(beginOffset)
        self.__block: bytes = block

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex + self.__beginOffset + self.__block

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def block(self) -> bytes:
        return self.__block
