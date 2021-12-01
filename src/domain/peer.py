class Peer:
    def __init__(self, IP: int, port: int):
        self.__IP: int = IP
        self.__port: int = port

    @property
    def IP(self) -> int:
        return self.__IP

    @property
    def port(self) -> int:
        return self.__port

    def __str__(self) -> str:
        firstOctet = (self.__IP // 256 ** 3) % 256
        secondOctet = (self.__IP // 256 ** 2) % 256
        thirdOctet = (self.__IP // 256 ** 1) % 256
        fourthOctet = self.__IP % 256
        return f'{firstOctet}.{secondOctet}.{thirdOctet}.{fourthOctet}:{self.__port}'

    def __eq__(self, other):
        return isinstance(other, Peer) and self.__IP == other.IP and self.__port == other.port
