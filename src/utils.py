import datetime
from asyncio import StreamReader, StreamWriter
from typing import Tuple, Final

MESSAGE_ID_LENGTH: Final[int] = 1  # bytes
HANDSHAKE_MESSAGE_LENGTH: Final[int] = 68  # bytes
INFINITY: Final[int] = 999999999


def convertIntegerTo4ByteBigEndian(intValue: int) -> bytes:
    return intValue.to_bytes(4, byteorder="big")


def convertByteToInteger(byteValue: bytes) -> int:
    return int.from_bytes(byteValue, "big")


def convertIntegerTo1Byte(intValue: int) -> bytes:
    return chr(intValue).encode()


def convertIPFromStringToInt(IP: str) -> int:
    splitBytes: list[str] = IP.split('.')
    return 256**3 * int(splitBytes[0]) + 256**2 * int(splitBytes[1]) + 256 * int(splitBytes[2]) + int(splitBytes[3])


def convertIPFromIntToString(IP: int) -> str:
    firstOctet = (IP // 256 ** 3) % 256
    secondOctet = (IP // 256 ** 2) % 256
    thirdOctet = (IP // 256 ** 1) % 256
    fourthOctet = IP % 256
    return f"""{firstOctet}.{secondOctet}.{thirdOctet}.{fourthOctet}"""


def convert4ByteBigEndianToInteger(byteValue: bytes) -> int:
    return int.from_bytes(byteValue, "big")


async def closeConnection(readerWriterTuple: Tuple[StreamReader, StreamWriter]) -> None:
    readerWriterTuple[1].close()
    await readerWriterTuple[1].wait_closed()


def prettyPrintSize(byteCount: float) -> str:
    RATIO: Final[int] = 1024

    KBCount: float = byteCount / RATIO
    if KBCount < 1.0:
        return f"{byteCount:.2f}B"
    
    MBCount: float = KBCount / RATIO
    if MBCount < 1.0:
        return f"{KBCount:.2f}KB"
    
    GBCount: float = MBCount / RATIO
    if GBCount < 1.0:
        return f"{MBCount:.2f}MB"
    
    TBCount: float = GBCount / RATIO
    if TBCount < 1.0:
        return f"{GBCount:.2f}GB"
    return f"{TBCount:.2f}TB"


def prettyPrintTime(seconds: int) -> str:
    return str(datetime.timedelta(seconds=seconds))
