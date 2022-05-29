from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class PieceMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 7
    PIECE_INDEX_LENGTH: Final[int] = 4  # bytes
    BEGIN_OFFSET_LENGTH: Final[int] = 4  # bytes
    BASE_LENGTH_PREFIX: Final[int] = utils.MESSAGE_ID_LENGTH + PIECE_INDEX_LENGTH + BEGIN_OFFSET_LENGTH

    def __init__(self, pieceIndex: int = 0, beginOffset: int = 0, block: bytes = b""):
        # pieceIndex and beginOffset are 0-indexed
        super().__init__(self.BASE_LENGTH_PREFIX + len(block), self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)
        self.__beginOffset: bytes = utils.convertIntegerTo4ByteBigEndian(beginOffset)
        self.__block: bytes = block

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex + self.__beginOffset + self.__block

    def setMessagePropertiesFromPayload(self, payload: bytes) -> None:
        self.__pieceIndex = payload[: self.PIECE_INDEX_LENGTH]
        self.__beginOffset = payload[self.PIECE_INDEX_LENGTH: self.PIECE_INDEX_LENGTH + self.BEGIN_OFFSET_LENGTH]
        self.__block = payload[self.PIECE_INDEX_LENGTH + self.BEGIN_OFFSET_LENGTH:]

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def block(self) -> bytes:
        return self.__block

    def __str__(self) -> str:
        return super().__str__() + f"piece index = {utils.convertByteToInteger(self.__pieceIndex)}; begin offset = {utils.convertByteToInteger(self.__beginOffset)}"
