from typing import Final
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class ChokeMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 0
    LENGTH_PREFIX: Final[int] = 1  # messageID = 1B

    def __init__(self):
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
