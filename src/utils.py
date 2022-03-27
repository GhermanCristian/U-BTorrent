def convertIntegerTo4ByteBigEndian(intValue: int) -> bytes:
    return intValue.to_bytes(4, byteorder="big")


def convertByteToInteger(byteValue: bytes) -> int:
    return int.from_bytes(byteValue, "big")


def convertIntegerTo1Byte(intValue: int) -> bytes:
    return chr(intValue).encode()


def convertIPFromStringToInt(IP: str) -> int:
    splitBytes: list[str] = IP.split('.')
    return 256**3 * int(splitBytes[0]) + 256**2 * int(splitBytes[1]) + 256 * int(splitBytes[2]) + int(splitBytes[3])
