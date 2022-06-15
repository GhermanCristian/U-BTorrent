import os
from typing import Tuple, List, Final
from domain.block import Block
from domain.file import File
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class TorrentDiskLoader:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner

    def __readFileSection(self, file: File, fileStartOffset: int, sectionLength: int) -> bytes | None:
        try:
            fileDescriptor: int = os.open(file.path, os.O_RDONLY | os.O_BINARY)
        except Exception:
            return None
        newPosition: int = os.lseek(fileDescriptor, fileStartOffset, os.SEEK_SET)
        if newPosition != fileStartOffset:
            os.close(fileDescriptor)
            return None
        readData: bytes = os.read(fileDescriptor, sectionLength)
        if len(readData) != sectionLength:
            os.close(fileDescriptor)
            return None
        os.close(fileDescriptor)
        return readData

    def __getFilesWhichContainEntity(self, entityStartOffset: int, entityEndOffset: int, entityLength: int) -> List[Tuple[File, int, int]]:
        fileListWithOffsets: List[Tuple[File, int, int]] = []  # file, file start offset, entity length in file
        currentFileStartOffset: int = 0

        for file in self.__scanner.files:
            currentFileEndOffset: int = currentFileStartOffset + file.length

            if entityStartOffset < currentFileStartOffset and currentFileEndOffset <= entityEndOffset:  # entire file is inside the piece
                fileListWithOffsets.append((file, 0, file.length))
            elif currentFileStartOffset <= entityStartOffset < currentFileEndOffset:
                if currentFileStartOffset < entityEndOffset <= currentFileEndOffset:  # entire piece is inside a file
                    fileListWithOffsets.append((file, entityStartOffset - currentFileStartOffset, entityLength))
                else:  # just the start is inside file
                    fileListWithOffsets.append((file, entityStartOffset - currentFileStartOffset, currentFileEndOffset - entityStartOffset))
            elif currentFileStartOffset < entityEndOffset <= currentFileEndOffset:  # just the end is inside file
                fileListWithOffsets.append((file, 0, entityEndOffset - currentFileStartOffset))

            currentFileStartOffset = currentFileEndOffset

        return fileListWithOffsets

    def __determineFilesWhichContainBlock(self, blockWithoutData: Block) -> List[Tuple[File, int, int]]:
        pieceIndex: int = blockWithoutData.pieceIndex
        blockStartOffset: int = blockWithoutData.beginOffset
        if pieceIndex > 0:
            blockStartOffset += (pieceIndex - 1) * self.__scanner.regularPieceLength
        blockEndOffset: int = blockStartOffset + blockWithoutData.length
        return self.__getFilesWhichContainEntity(blockStartOffset, blockEndOffset, blockWithoutData.length)

    def __determineFilesWhichContainPiece(self, pieceIndex: int) -> List[Tuple[File, int, int]]:
        pieceLength: int = self.__scanner.regularPieceLength
        if pieceIndex == self.__scanner.pieceCount - 1:
            pieceLength = self.__scanner.finalPieceLength
        pieceStartOffset: int = pieceIndex * self.__scanner.regularPieceLength
        pieceEndOffset: int = pieceStartOffset + pieceLength
        return self.__getFilesWhichContainEntity(pieceStartOffset, pieceEndOffset, pieceLength)

    def __getDataForFileListAndOffsets(self, fileListAndOffsets: List[Tuple[File, int, int]]) -> bytes:
        READING_ATTEMPTS: Final[int] = 2

        dataReadSoFar: bytes = b""
        for file, fileStartOffset, entitySectionLength in fileListAndOffsets:
            for _ in range(READING_ATTEMPTS):
                readData: bytes | None = self.__readFileSection(file, fileStartOffset, entitySectionLength)
                if readData is not None:
                    dataReadSoFar += readData
                    break
        return dataReadSoFar

    def getDataForPiece(self, pieceIndex: int) -> bytes:
        return self.__getDataForFileListAndOffsets(self.__determineFilesWhichContainPiece(pieceIndex))

    def getDataForBlock(self, blockWithoutData: Block) -> bytes:
        return self.__getDataForFileListAndOffsets(self.__determineFilesWhichContainBlock(blockWithoutData))
