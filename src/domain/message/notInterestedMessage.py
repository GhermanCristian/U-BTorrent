from typing import Final


class NotInterestedMessage:
    MESSAGE_ID: Final[int] = 3

    def __init__(self):
        self.__content: bytes = chr(self.MESSAGE_ID).encode()

    def getMessage(self) -> bytes:
        return self.__content

    def __eq__(self, otherMessage):
        return isinstance(otherMessage, NotInterestedMessage) and self.__content == otherMessage.__content

    def __hash__(self):
        return hash(self.__content)
