from asyncio import StreamReader, StreamWriter
from typing import Tuple


def convertIntegerTo4ByteBigEndian(intValue: int) -> bytes:
    return intValue.to_bytes(4, byteorder="big")


def convertByteToInteger(byteValue: bytes) -> int:
    return int.from_bytes(byteValue, "big")


def convertIntegerTo1Byte(intValue: int) -> bytes:
    return chr(intValue).encode()


def convertIPFromStringToInt(IP: str) -> int:
    splitBytes: list[str] = IP.split('.')
    return 256**3 * int(splitBytes[0]) + 256**2 * int(splitBytes[1]) + 256 * int(splitBytes[2]) + int(splitBytes[3])


def convert4ByteBigEndianToInteger(byteValue: bytes) -> int:
    return int.from_bytes(byteValue, "big")


async def closeConnection(readerWriterTuple: Tuple[StreamReader, StreamWriter]) -> None:
    readerWriterTuple[1].close()
    await readerWriterTuple[1].wait_closed()
