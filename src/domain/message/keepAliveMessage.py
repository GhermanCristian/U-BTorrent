class KeepAliveMessage:
    def __init__(self):
        self.__content: bytes = b""

    def getMessage(self) -> bytes:
        return self.__content

    def __eq__(self, otherMessage):
        return isinstance(otherMessage, KeepAliveMessage) and self.__content == otherMessage.__content

    def __hash__(self):
        return hash(self.__content)
