from asyncio import StreamReader, StreamWriter
from typing import Tuple, Final

MESSAGE_ID_LENGTH: Final[int] = 1  # bytes
HANDSHAKE_MESSAGE_LENGTH: Final[int] = 68  # bytes


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
