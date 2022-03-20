import unittest
from typing import Final
from domain.validator.handshakeResponseValidator import HandshakeResponseValidator


class TestHandshakeResponseValidator(unittest.TestCase):
    CURRENT_PROTOCOL: Final[bytes] = b"BitTorrent protocol"
    INFO_HASH: Final[bytes] = b"\xa4\x0e\xf4\x82 ,I\xc1~\xe6\x0e\x99\xb8\xc2\xff\xb2\x99+d\xc4"

    def setUp(self) -> None:
        self.__handshakeResponseValidator = HandshakeResponseValidator(self.INFO_HASH, self.CURRENT_PROTOCOL)

    def test_validateHandshakeResponse_ValidHandshake_PassesValidation(self) -> None:
        handshakeResponse: bytes = b"\x13BitTorrent protocol\x00\x00\x00\x00\x00\x10\x00\x04\xa4\x0e\xf4\x82 ,I\xc1~\xe6\x0e\x99\xb8\xc2\xff\xb2\x99+d\xc4-TR3000-9t3ra3wj5oup"
        self.assertTrue(self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse))

    def test_validateHandshakeResponse_EmptyHandshake_FailsValidation(self) -> None:
        handshakeResponse: bytes = b""
        self.assertFalse(self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse))

    def test_validateHandshakeResponse_HandshakeDoesNotStartWithProtocolLength_FailsValidation(self) -> None:
        handshakeResponse: bytes = b"\x14BitTorrent protocol\x00\x00\x00\x00\x00\x10\x00\x04\xa4\x0e\xf4\x82 ,I\xc1~\xe6\x0e\x99\xb8\xc2\xff\xb2\x99+d\xc4-TR3000-9t3ra3wj5oup"
        self.assertFalse(self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse))

    def test_validateHandshakeResponse_InvalidProtocol_FailsValidation(self) -> None:
        handshakeResponse: bytes = b"\x13BitTorrent protccol\x00\x00\x00\x00\x00\x10\x00\x04\xa4\x0e\xf4\x82 ,I\xc1~\xe6\x0e\x99\xb8\xc2\xff\xb2\x99+d\xc4-TR3000-9t3ra3wj5oup"
        self.assertFalse(self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse))

    def test_validateHandshakeResponse_InfoHashDoesNotMatch_FailsValidation(self) -> None:
        handshakeResponse: bytes = b"\x13BitTorrent protocol\x00\x00\x00\x00\x00\x10\x00\x04\xa4\x0e\xf4\x82 ,I\xc1~\xf6\x0e\x99\xb8\xc2\xff\xb2\x99+d\xc4-TR3000-9t3ra3wj5oup"
        self.assertFalse(self.__handshakeResponseValidator.validateHandshakeResponse(handshakeResponse))


if __name__ == '__main__':
    unittest.main()
