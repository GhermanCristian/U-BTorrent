from typing import Final
import utils
from domain.message.messageWithLengthAndID import MessageWithLengthAndID


class NotInterestedMessage(MessageWithLengthAndID):
    MESSAGE_ID: Final[int] = 3
    LENGTH_PREFIX: Final[int] = utils.MESSAGE_ID_LENGTH

    def __init__(self):
        super().__init__(self.LENGTH_PREFIX, self.MESSAGE_ID)
