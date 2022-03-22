from abc import abstractmethod, ABC


class Message(ABC):  # ABC = abstract base class
    @abstractmethod
    def getMessageContent(self) -> bytes:
        pass

    def __hash__(self) -> int:
        return hash(self.getMessageContent())

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.getMessageContent() == other.getMessageContent()