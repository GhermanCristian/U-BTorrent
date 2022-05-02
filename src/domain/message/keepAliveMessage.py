from typing import Final
import utils
from domain.message.message import Message


class KeepAliveMessage(Message):
    LENGTH_PREFIX: Final[int] = 0

    def __init__(self):
        self.__content: bytes = utils.convertIntegerTo4ByteBigEndian(self.LENGTH_PREFIX)

    def getMessageContent(self) -> bytes:
        return self.__content
