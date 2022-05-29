from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID
from bitarray import bitarray


class BitfieldMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 5
    BASE_LENGTH_PREFIX: Final[int] = utils.MESSAGE_ID_LENGTH

    def __init__(self, bitfield: bitarray = bitarray()):
        super().__init__(self.BASE_LENGTH_PREFIX + len(bitfield), self.MESSAGE_ID)
        self.__bitfield: bytes = bitfield.tobytes()

    def getMessageContent(self) -> bytes:
        return super().getMessageContent() + self.__bitfield

    def setMessagePropertiesFromPayload(self, payload: bytes) -> None:
        self.__bitfield = payload

    @property
    def bitfield(self) -> bytes:
        return self.__bitfield

    def __str__(self) -> str:
        return super().__str__() + f"bitfield: {self.__bitfield}"
