from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class RequestMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 6
    LENGTH_PREFIX: Final[int] = 13  # messageID = 1B; pieceIndex, beginOffset, blockLength = 4B each

    def __init__(self, pieceIndex: int = 0, beginOffset: int = 0, blockLength: int = 0):
        # pieceIndex and beginOffset are 0-indexed
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)
        self.__beginOffset: bytes = utils.convertIntegerTo4ByteBigEndian(beginOffset)
        self.__blockLength: bytes = utils.convertIntegerTo4ByteBigEndian(blockLength)

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex + self.__beginOffset + self.__blockLength

    def setMessagePropertiesFromPayload(self, payload: bytes) -> None:
        self.__pieceIndex = payload[0: 4]
        self.__beginOffset = payload[4: 8]
        self.__blockLength = payload[8: 12]

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
