import unittest
from typing import Final
from domain.file import File
from torrentMetaInfoScanner import TorrentMetaInfoScanner


class TestValidTorrentMetaInfoScanner(unittest.TestCase):
    TORRENT_META_INFO_FILE_LOCATION: Final[str] = "../Resources/NBALOGO_archive.torrent"

    def __loadTorrentMetaInfoFile(self, torrentFileLocation: str):
        self.__torrentMetaInfo = TorrentMetaInfoScanner(torrentFileLocation)

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def setUp(self) -> None:
        self.__loadTorrentMetaInfoFile(self.TORRENT_META_INFO_FILE_LOCATION)

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_getAnnounceURL_ValidAnnounceURL_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getAnnounceURL(), "http://bt1.archive.org:6969/announce")

    def test_getAnnounceURLList_ValidAnnounceURLList_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getAnnounceURLList(), [["http://bt1.archive.org:6969/announce"], ["http://bt2.archive.org:6969/announce"]])

    def test_getTorrentName_ValidTorrentName_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getTorrentName(), "NBALOGO")

    def test_getPieceLength_ValidPieceLength_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getPieceLength(), 524288)

    def test_getPieces_ValidPieces_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getPieces(), b"\x88,;\xe3\xd3&*V\xaa\xa0\x047\x1d\x9fI\x16\xa5\x85 8")

    def test_getFiles_ValidFiles_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getFiles(), [File("NBALOGO.png", "16d3347ef91314e5fbd7fcdb2635ba06da69defd", 19764),
                                                             File("NBALOGO_meta.sqlite", "6b499be50d7dc92e56d6c5c9b58c04c01777c12f", 9216),
                                                             File("NBALOGO_meta.xml", "f9df69bb487033d01e75450bcef41ebc8daf53df", 635),
                                                             File("NBALOGO_thumb.jpg", "ae697ce30a9ad8a7db9f6a945c7e439850efb805", 4389),
                                                             File("__ia_thumb.jpg", "cbe3f80e4f1ae8d6ebfa8a0052acae25b04691f5", 8971)])

    def test_getInfoHash_ValidInfoHash_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getInfoHash(), b"w\x0e\xc6]\xe8T\xa16Pw\xea\xdaBL2\x86\xc6IK\x95")

    def test_getTotalContentSize_ValidContent_CorrectResult(self) -> None:
        self.assertEqual(self.__torrentMetaInfo.getTotalContentSize(), 42975)


if __name__ == '__main__':
    unittest.main()
