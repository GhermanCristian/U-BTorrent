from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class RequestMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 6
    PIECE_INDEX_LENGTH: Final[int] = 4  # bytes
    BEGIN_OFFSET_LENGTH: Final[int] = 4  # bytes
    BLOCK_LENGTH_LENGTH: Final[int] = 4  # bytes
    LENGTH_PREFIX: Final[int] = utils.MESSAGE_ID_LENGTH + PIECE_INDEX_LENGTH + BEGIN_OFFSET_LENGTH + BLOCK_LENGTH_LENGTH

    def __init__(self, pieceIndex: int = 0, beginOffset: int = 0, blockLength: int = 0):
        # pieceIndex and beginOffset are 0-indexed
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)
        self.__beginOffset: bytes = utils.convertIntegerTo4ByteBigEndian(beginOffset)
        self.__blockLength: bytes = utils.convertIntegerTo4ByteBigEndian(blockLength)

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex + self.__beginOffset + self.__blockLength

    def setMessagePropertiesFromPayload(self, payload: bytes) -> None:
        BEGIN_OFFSET_START_INDEX: Final[int] = self.PIECE_INDEX_LENGTH
        BLOCK_LENGTH_START_INDEX: Final[int] = BEGIN_OFFSET_START_INDEX + self.BEGIN_OFFSET_LENGTH
        BLOCK_LENGTH_END_INDEX: Final[int] = BLOCK_LENGTH_START_INDEX + self.BLOCK_LENGTH_LENGTH

        self.__pieceIndex = payload[: BEGIN_OFFSET_START_INDEX]
        self.__beginOffset = payload[BEGIN_OFFSET_START_INDEX: BLOCK_LENGTH_START_INDEX]
        self.__blockLength = payload[BLOCK_LENGTH_START_INDEX: BLOCK_LENGTH_END_INDEX]

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def blockLength(self) -> bytes:
        return self.__blockLength

    def __str__(self) -> str:
        return super().__str__() + f"piece index = {utils.convertByteToInteger(self.__pieceIndex)}; begin offset = {utils.convertByteToInteger(self.__beginOffset)}; block length = {utils.convertByteToInteger(self.__blockLength)}"
