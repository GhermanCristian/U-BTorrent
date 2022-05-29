import os
import unittest
from typing import Final
from domain.file import File
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class TestTorrentMetaInfoScanner(unittest.TestCase):
    TORRENT_META_INFO_FILE_LOCATION: Final[str] = "..\\Resources\\Test\\NBALOGO_archive.torrent"
    TORRENT_TEST_DOWNLOAD_LOCATION: Final[str] = "..\\Resources\\Test\\Downloads"
    TORRENT_NAME: Final[str] = "NBALOGO"

    def setUp(self) -> None:
        self.__scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner(self.TORRENT_META_INFO_FILE_LOCATION, self.TORRENT_TEST_DOWNLOAD_LOCATION)

    def tearDown(self) -> None:
        self.__scanner.removeRootDownloadFolder()

    def test_announceURL_ValidAnnounceURL_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.announceURL, "http://bt1.archive.org:6969/announce")

    def test_announceURLList_ValidAnnounceURLList_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.announceURLList, [["http://bt1.archive.org:6969/announce"], ["http://bt2.archive.org:6969/announce"]])

    def test_torrentName_ValidTorrentName_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.torrentName, self.TORRENT_NAME)

    def test_regularPieceLength_ValidRegularPieceLength_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.regularPieceLength, 524288)

    def test_pieceCount_ValidPieceCount_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.pieceCount, 1)

    def test_finalPieceLength_ValidFinalPieceLength_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.finalPieceLength, 42975)

    def test_pieces_ValidPieces_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.pieces, b"\x88,;\xe3\xd3&*V\xaa\xa0\x047\x1d\x9fI\x16\xa5\x85 8")

    def test_files_ValidFiles_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.files, [File(os.path.join(self.TORRENT_TEST_DOWNLOAD_LOCATION, self.TORRENT_NAME, "NBALOGO.png"), 19764),
                                                File(os.path.join(self.TORRENT_TEST_DOWNLOAD_LOCATION, self.TORRENT_NAME, "NBALOGO_meta.sqlite"), 9216),
                                                File(os.path.join(self.TORRENT_TEST_DOWNLOAD_LOCATION, self.TORRENT_NAME, "NBALOGO_meta.xml"), 635),
                                                File(os.path.join(self.TORRENT_TEST_DOWNLOAD_LOCATION, self.TORRENT_NAME, "NBALOGO_thumb.jpg"), 4389),
                                                File(os.path.join(self.TORRENT_TEST_DOWNLOAD_LOCATION, self.TORRENT_NAME, "__ia_thumb.jpg"), 8971)])

    def test_infoHash_ValidInfoHash_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.infoHash, b"w\x0e\xc6]\xe8T\xa16Pw\xea\xdaBL2\x86\xc6IK\x95")

    def test_getTotalContentSize_ValidContent_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.getTotalContentSize(), 42975)

    def test_getPieceHash_ValidPieceHashIndex0_CorrectResult(self) -> None:
        self.assertEqual(self.__scanner.getPieceHash(0), b"\x88,;\xe3\xd3&*V\xaa\xa0\x047\x1d\x9fI\x16\xa5\x85 8")


if __name__ == '__main__':
    unittest.main()
