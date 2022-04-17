import asyncio
import os
from typing import List, Tuple
from domain.file import File
from domain.piece import Piece
from torrentMetaInfoScanner import TorrentMetaInfoScanner


class TorrentSaver:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__torrentName: str = scanner.getTorrentName()
        self.__torrentFiles: List[File] = scanner.getFiles()
        self.__piecesQueue: asyncio.Queue[Piece] = asyncio.Queue()
        self.__pieceLength: int = scanner.getPieceLength()
        self.__finalPieceLength: int = scanner.getFinalPieceLength()
        self.__pieceCount: int = scanner.getPieceCount()
        self.__task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    def putPieceInQueue(self, piece: Piece) -> None:
        self.__piecesQueue.put_nowait(piece)

    def __determineFilesWhichContainPiece(self, piece: Piece) -> List[Tuple[File, int, int, int]]:
        # TODO - handle the case where there are empty files
        fileListWithOffsets: List[Tuple[File, int, int, int]] = []  # file offset, piece start, piece section length
        pieceLength: int = self.__pieceLength
        if piece.index == self.__pieceCount - 1:
            pieceLength = self.__finalPieceLength
        pieceStartOffset: int = piece.index * self.__pieceLength
        pieceEndOffset: int = pieceStartOffset + pieceLength
        currentFileStartOffset: int = 0
        for file in self.__torrentFiles:
            currentFileEndOffset: int = currentFileStartOffset + file.length

            if pieceStartOffset < currentFileStartOffset and currentFileEndOffset <= pieceEndOffset:  # entire file is inside the piece
                fileListWithOffsets.append((file, 0, currentFileStartOffset - pieceStartOffset, file.length))

            elif currentFileStartOffset <= pieceStartOffset < currentFileEndOffset:
                if currentFileStartOffset < pieceEndOffset <= currentFileEndOffset:  # entire piece is inside a file
                    fileListWithOffsets.append((file, pieceStartOffset - currentFileStartOffset, 0, pieceLength))
                else:  # just the start is inside file
                    fileListWithOffsets.append((file, pieceStartOffset - currentFileStartOffset, 0, currentFileEndOffset - pieceStartOffset))

            elif currentFileStartOffset < pieceEndOffset <= currentFileEndOffset:  # just the end is inside file
                fileListWithOffsets.append((file, 0, pieceLength + currentFileStartOffset - pieceEndOffset, pieceEndOffset - currentFileStartOffset))

            currentFileStartOffset = currentFileEndOffset
            
        return fileListWithOffsets

    def __writePieceSectionToFile(self, file: File, piece: Piece, fileStartOffset: int, pieceStartOffset: int, pieceSectionLength: int) -> None:
        fileDescriptor: int = os.open(file.path, os.O_RDWR | os.O_CREAT)
        newPosition: int = os.lseek(fileDescriptor, fileStartOffset, os.SEEK_SET)
        if newPosition != fileStartOffset:
            print("did not seek all")
        writtenByteCount: int = os.write(fileDescriptor, piece.data[pieceStartOffset: pieceStartOffset + pieceSectionLength])
        if writtenByteCount != pieceSectionLength:
            print("did not write all")
        os.close(fileDescriptor)

    async def __run(self) -> None:
        while True:
            piece: Piece = await self.__piecesQueue.get()
            if not piece:
                print("Bad piece")
                return

            fileListWithOffsets: List[Tuple[File, int, int, int]] = self.__determineFilesWhichContainPiece(piece)
            for file, fileStartOffset, pieceStartOffset, pieceSectionLength in fileListWithOffsets:
                self.__writePieceSectionToFile(file, piece, fileStartOffset, pieceStartOffset, pieceSectionLength)
            piece.clear()
