import hashlib
from typing import List, Tuple, Final
import utils
from domain.file import File
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class TorrentChecker:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner

    def __determineFilesWhichContainPiece(self, pieceIndex: int) -> List[Tuple[File, int, int]]:
        # file offset, piece start, piece section length
        fileListWithOffsets: List[Tuple[File, int, int]] = []

        pieceLength: int = self.__scanner.regularPieceLength
        if pieceIndex == self.__scanner.pieceCount - 1:
            pieceLength = self.__scanner.finalPieceLength
        pieceStartOffset: int = pieceIndex * self.__scanner.regularPieceLength
        pieceEndOffset: int = pieceStartOffset + pieceLength
        currentFileStartOffset: int = 0
        for file in self.__scanner.files:
            currentFileEndOffset: int = currentFileStartOffset + file.length

            if pieceStartOffset < currentFileStartOffset and currentFileEndOffset <= pieceEndOffset:  # entire file is inside the piece
                fileListWithOffsets.append((file, 0, file.length))
            elif currentFileStartOffset <= pieceStartOffset < currentFileEndOffset:
                if currentFileStartOffset < pieceEndOffset <= currentFileEndOffset:  # entire piece is inside a file
                    fileListWithOffsets.append((file, pieceStartOffset - currentFileStartOffset, pieceLength))
                else:  # just the start is inside file
                    fileListWithOffsets.append((file, pieceStartOffset - currentFileStartOffset, currentFileEndOffset - pieceStartOffset))
            elif currentFileStartOffset < pieceEndOffset <= currentFileEndOffset:  # just the end is inside file
                fileListWithOffsets.append((file, 0, pieceEndOffset - currentFileStartOffset))

            currentFileStartOffset = currentFileEndOffset

        return fileListWithOffsets

    def __getDataForPiece(self, pieceIndex: int) -> bytes:
        READING_ATTEMPTS: Final[int] = 2

        pieceData: bytes = b""
        for file, fileStartOffset, pieceSectionLength in self.__determineFilesWhichContainPiece(pieceIndex):
            for _ in range(READING_ATTEMPTS):
                readData: bytes | None = utils.readFileSection(file, fileStartOffset, pieceSectionLength)
                if readData is not None:
                    pieceData += readData
                    break
        return pieceData

    def getPiecesWrittenOnDisk(self) -> List[bool]:
        piecesWrittenOnDisk: List[bool] = []
        for pieceIndex in range(self.__scanner.pieceCount):
            pieceData: bytes = self.__getDataForPiece(pieceIndex)
            actualPieceHash: bytes = hashlib.sha1(pieceData).digest()
            expectedPieceHash: bytes = self.__scanner.getPieceHash(pieceIndex)
            piecesWrittenOnDisk.append(actualPieceHash == expectedPieceHash)
        return piecesWrittenOnDisk
