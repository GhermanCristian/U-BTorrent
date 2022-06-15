from abc import abstractmethod, ABC
from domain.peer import Peer


class Message(ABC):  # ABC = abstract base class
    @abstractmethod
    def getMessageContent(self) -> bytes:
        pass

    async def send(self, otherPeer: Peer) -> None:
        try:
            otherPeer.streamWriter.write(self.getMessageContent())
            await otherPeer.streamWriter.drain()
        except Exception as e:
            pass  # TODO - log the exception

    def __hash__(self) -> int:
        return hash(self.getMessageContent())

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.getMessageContent() == other.getMessageContent()

    def __str__(self) -> str:
        return str(self.getMessageContent())
