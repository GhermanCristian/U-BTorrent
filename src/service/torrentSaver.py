import asyncio
import os
from asyncio import Task
from typing import List, Tuple
from domain.file import File
from domain.piece import Piece
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class TorrentSaver:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__torrentName: str = scanner.torrentName
        self.__torrentFiles: List[File] = scanner.files
        self.__piecesQueue: asyncio.Queue[Piece] = asyncio.Queue()
        self.__regularPieceLength: int = scanner.regularPieceLength
        self.__finalPieceLength: int = scanner.finalPieceLength
        self.__pieceCount: int = scanner.pieceCount
        self.__isDownloadComplete: bool = False

    def start(self) -> None:
        task: Task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    """
    Puts the current piece in the queue of pieces to be written to disk
    """
    def putPieceInQueue(self, piece: Piece) -> None:
        self.__piecesQueue.put_nowait(piece)

    def setDownloadComplete(self) -> None:
        self.__isDownloadComplete = True

    """
    Computes a list of files which contain the given piece
    @:param piece - the piece whose files are determined
    @:return a tuple which contains:
        file offset - the position at which writing starts in the current file
        piece start - the position at which the piece starts for the current file
        piece section length - the length of the piece section associated with the current file
    """
    def __determineFilesWhichContainPiece(self, piece: Piece) -> List[Tuple[File, int, int, int]]:
        # TODO - handle the case where there are empty files
        fileListWithOffsets: List[Tuple[File, int, int, int]] = []

        pieceLength: int = self.__regularPieceLength
        if piece.index == self.__pieceCount - 1:
            pieceLength = self.__finalPieceLength
        pieceStartOffset: int = piece.index * self.__regularPieceLength
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

    """
    Writes a piece section to disk
    @:param file - the file this piece section belongs to
    @:param piece - the piece whose section is written to disk
    @:param fileStartOffset - the position in which to start writing to the file
    @:param pieceSectionLength - the length of the section to be written
    @:return True, if the data is successfully written to disk, False otherwise
    """
    def __writePieceSectionToDisk(self, file: File, piece: Piece, fileStartOffset: int, pieceStartOffset: int, pieceSectionLength: int) -> bool:
        fileDescriptor: int = os.open(file.path, os.O_RDWR | os.O_CREAT | os.O_BINARY)
        newPosition: int = os.lseek(fileDescriptor, fileStartOffset, os.SEEK_SET)
        if newPosition != fileStartOffset:
            os.close(fileDescriptor)
            return False
        writtenByteCount: int = os.write(fileDescriptor, piece.data[pieceStartOffset: pieceStartOffset + pieceSectionLength])
        if writtenByteCount != pieceSectionLength:
            os.close(fileDescriptor)
            return False
        os.close(fileDescriptor)
        return True

    async def __run(self) -> None:
        while not (self.__isDownloadComplete and self.__piecesQueue.empty()):
            piece: Piece = await self.__piecesQueue.get()
            if not piece:
                return

            fileListWithOffsets: List[Tuple[File, int, int, int]] = self.__determineFilesWhichContainPiece(piece)
            for file, fileStartOffset, pieceStartOffset, pieceSectionLength in fileListWithOffsets:
                while not self.__writePieceSectionToDisk(file, piece, fileStartOffset, pieceStartOffset, pieceSectionLength):
                    pass
            piece.clear()
