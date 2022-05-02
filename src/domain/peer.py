from asyncio import StreamReader, StreamWriter
from typing import List
from bitarray import bitarray
import utils
from domain.block import Block


class Peer:
    def __init__(self, IP: int, port: int):
        # IP + port uniquely determine the peer (for example, __eq__ won't check choking / interested, same for __hash__)
        self.__IP: int = IP
        self.__port: int = port
        self.__amChokingIt: bool = True
        self.__isChokingMe: bool = True
        self.__amInterestedInIt: bool = False
        self.__isInterestedInMe: bool = False
        self.__availablePieces: bitarray = bitarray()
        self.__streamReader: StreamReader | None = None
        self.__streamWriter: StreamWriter | None = None
        self.__blocksRequestedFromPeer: List[Block] = []

    @property
    def IP(self) -> int:
        return self.__IP

    @property
    def port(self) -> int:
        return self.__port

    @property
    def amChokingIt(self) -> bool:
        return self.__amChokingIt

    @amChokingIt.setter
    def amChokingIt(self, newValue: bool) -> None:
        self.__amChokingIt = newValue

    @property
    def isChokingMe(self) -> bool:
        return self.__isChokingMe

    @isChokingMe.setter
    def isChokingMe(self, newValue: bool) -> None:
        self.__isChokingMe = newValue

    @property
    def amInterestedInIt(self) -> bool:
        return self.__amInterestedInIt

    @amInterestedInIt.setter
    def amInterestedInIt(self, newValue: bool) -> None:
        self.__amInterestedInIt = newValue

    @property
    def isInterestedInMe(self) -> bool:
        return self.__isInterestedInMe

    @isInterestedInMe.setter
    def isInterestedInMe(self, newValue: bool) -> None:
        self.__isInterestedInMe = newValue

    @property
    def availablePieces(self) -> bitarray:
        return self.__availablePieces

    @availablePieces.setter
    def availablePieces(self, newValue: bitarray) -> None:
        self.__availablePieces = newValue

    @property
    def streamReader(self) -> StreamReader:
        return self.__streamReader

    @streamReader.setter
    def streamReader(self, newReader: StreamReader) -> None:
        self.__streamReader = newReader

    @property
    def streamWriter(self) -> StreamWriter:
        return self.__streamWriter

    @streamWriter.setter
    def streamWriter(self, newWriter: StreamWriter) -> None:
        self.__streamWriter = newWriter

    @property
    def blocksRequestedFromPeer(self) -> List[Block]:
        return self.__blocksRequestedFromPeer

    async def closeConnection(self) -> None:
        if self.hasActiveConnection():
            try:
                await utils.closeConnection((self.__streamReader, self.__streamWriter))
            except Exception as e:
                print(e)
        self.__streamReader, self.__streamWriter = None, None

    def hasActiveConnection(self) -> bool:
        return self.__streamReader is not None and self.__streamWriter is not None

    def getIPRepresentedAsString(self) -> str:
        firstOctet = (self.__IP // 256 ** 3) % 256
        secondOctet = (self.__IP // 256 ** 2) % 256
        thirdOctet = (self.__IP // 256 ** 1) % 256
        fourthOctet = self.__IP % 256
        return f"""{firstOctet}.{secondOctet}.{thirdOctet}.{fourthOctet}"""

    def __str__(self) -> str:
        return self.getIPRepresentedAsString() + f""":{self.__port};
            amChokingIt={self.__amChokingIt}; isChokingMe={self.__isChokingMe};
            amInterestedInIt={self.__amInterestedInIt}; isInterestedInMe={self.__isInterestedInMe};"""

    def __eq__(self, other):
        return isinstance(other, Peer) and self.__IP == other.IP and self.__port == other.port

    def __hash__(self):
        return hash((self.__IP, self.__port))
