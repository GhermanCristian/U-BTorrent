def convertIntegerTo4ByteBigEndian(intValue: int) -> bytes:
    return intValue.to_bytes(4, byteorder="big")


def convertIntegerTo1Byte(intValue: int) -> bytes:
    return chr(intValue).encode()
