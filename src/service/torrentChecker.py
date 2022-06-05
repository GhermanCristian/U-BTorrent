import hashlib
from typing import List
from service.torrentDiskLoader import TorrentDiskLoader
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class TorrentChecker:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner
        self.__torrentDiskLoader: TorrentDiskLoader = TorrentDiskLoader(scanner)

    def getPiecesWrittenOnDisk(self) -> List[bool]:
        piecesWrittenOnDisk: List[bool] = []
        for pieceIndex in range(self.__scanner.pieceCount):
            pieceData: bytes = self.__torrentDiskLoader.getDataForPiece(pieceIndex)
            actualPieceHash: bytes = hashlib.sha1(pieceData).digest()
            expectedPieceHash: bytes = self.__scanner.getPieceHash(pieceIndex)
            piecesWrittenOnDisk.append(actualPieceHash == expectedPieceHash)
        return piecesWrittenOnDisk
