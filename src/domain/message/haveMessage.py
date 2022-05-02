from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class HaveMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 4
    PIECE_INDEX_LENGTH: Final[int] = 4  # bytes
    LENGTH_PREFIX: Final[int] = utils.MESSAGE_ID_LENGTH + PIECE_INDEX_LENGTH

    def __init__(self, pieceIndex: int = 0):
        # pieceIndex is 0-indexed
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
        self.__pieceIndex: bytes = utils.convertIntegerTo4ByteBigEndian(pieceIndex)

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__pieceIndex

    def setMessagePropertiesFromPayload(self, payload: bytes) -> None:
        self.__pieceIndex = payload

    @property
    def pieceIndex(self) -> bytes:
        return self.__pieceIndex

    def __str__(self) -> str:
        return super().__str__() + f"piece index = {utils.convertByteToInteger(self.__pieceIndex)}"
