from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class CancelMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 8
    LENGTH_PREFIX: Final[int] = 13  # messageID = 1B; pieceIndex, beginOffset, pieceLength = 4B each

    def __init__(self, pieceIndex: int = 0, beginOffset: int = 0, pieceLength: int = 0):
        # pieceIndex and beginOffset are 0-indexed
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)
        self.__beginOffset: bytes = utils.convertIntegerTo4ByteBigEndian(beginOffset)
        self.__pieceLength: bytes = utils.convertIntegerTo4ByteBigEndian(pieceLength)

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex + self.__beginOffset + self.__pieceLength

    def setMessagePropertiesFromPayload(self, payload: bytes) -> None:
        self.__pieceIndex = payload[0: 4]
        self.__beginOffset = payload[4: 8]
        self.__pieceLength = payload[8: 12]

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    @property
    def beginOffset(self) -> bytes:
        return self.__beginOffset

    @property
    def pieceLength(self) -> bytes:
        return self.__pieceLength

    def __str__(self) -> str:
        return super().__str__() + f"piece index = {utils.convertByteToInteger(self.__pieceIndex)}; begin offset = {utils.convertByteToInteger(self.__beginOffset)}; piece length = {utils.convertByteToInteger(self.__pieceLength)}"
