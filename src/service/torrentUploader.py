import asyncio
import os
from asyncio import Task
from typing import List, Tuple
from domain.block import Block
from domain.file import File
from domain.message.pieceMessage import PieceMessage
from domain.peer import Peer


class TorrentUploader:
    def __init__(self, files: List[File], regularPieceLength: int):
        self.__files: List[File] = files
        self.__regularPieceLength: int = regularPieceLength
        self.__blockAndPeerQueue: asyncio.Queue[Tuple[Block, Peer]] = asyncio.Queue()
        self.__running: bool = False

    def start(self) -> None:
        self.__running = True
        task: Task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    """This can be called even if the uploader was not started yet"""
    def stop(self) -> None:
        self.__running = False

    def putBlockInQueue(self, blockWithoutData: Block, requester: Peer) -> None:
        self.__blockAndPeerQueue.put_nowait((blockWithoutData, requester))

    def __determineFilesWhichContainBlock(self, blockWithoutData: Block) -> List[Tuple[File, int, int]]:
        # file, start offset in file, block section length
        pieceIndex: int = blockWithoutData.pieceIndex
        blockGlobalStartOffset: int = blockWithoutData.beginOffset
        if pieceIndex > 0:
            blockGlobalStartOffset += (pieceIndex - 1) * self.__regularPieceLength
        blockGlobalEndOffset: int = blockGlobalStartOffset + blockWithoutData.length
        currentFileGlobalStartOffset: int = 0
        fileListWithOffsets: List[Tuple[File, int, int]] = []

        for file in self.__files:
            currentFileGlobalEndOffset: int = currentFileGlobalStartOffset + file.length

            if blockGlobalStartOffset < currentFileGlobalStartOffset and currentFileGlobalEndOffset <= blockGlobalEndOffset:  # entire file is inside the block
                fileListWithOffsets.append((file, 0, file.length))
            elif currentFileGlobalStartOffset <= blockGlobalStartOffset < currentFileGlobalEndOffset:
                if currentFileGlobalStartOffset < blockGlobalEndOffset <= currentFileGlobalEndOffset:  # entire block is inside a file
                    fileListWithOffsets.append((file, blockGlobalStartOffset - currentFileGlobalStartOffset, blockWithoutData.length))
                else:  # just the start is inside the file
                    fileListWithOffsets.append((file, blockGlobalStartOffset - currentFileGlobalStartOffset, currentFileGlobalEndOffset - blockGlobalStartOffset))
            elif currentFileGlobalStartOffset < blockGlobalEndOffset <= currentFileGlobalEndOffset:  # just the end is inside file
                fileListWithOffsets.append((file, 0, blockGlobalEndOffset - currentFileGlobalStartOffset))

            currentFileGlobalStartOffset = currentFileGlobalEndOffset

        return fileListWithOffsets

    def __readFileSection(self, file: File, fileStartOffset: int, blockSectionLength: int) -> bytes | None:
        fileDescriptor: int = os.open(file.path, os.O_RDONLY | os.O_BINARY)
        newPosition: int = os.lseek(fileDescriptor, fileStartOffset, os.SEEK_SET)
        if newPosition != fileStartOffset:
            os.close(fileDescriptor)
            return None
        readData: bytes = os.read(fileDescriptor, blockSectionLength)
        if len(readData) != blockSectionLength:
            os.close(fileDescriptor)
            return None
        os.close(fileDescriptor)
        return readData

    def __getBlockDataFromDisk(self, blockWithoutData: Block) -> bytes:
        fileListWithOffsets: List[Tuple[File, int, int]] = self.__determineFilesWhichContainBlock(blockWithoutData)
        dataReadSoFar: bytes = b""
        for file, fileStartOffset, blockSectionLength in fileListWithOffsets:
            readData: bytes | None = self.__readFileSection(file, fileStartOffset, blockSectionLength)
            while readData is None:
                readData = self.__readFileSection(file, fileStartOffset, blockSectionLength)
            dataReadSoFar += readData
        return dataReadSoFar

    async def __run(self) -> None:
        while self.__running:
            blockAndPeer: Tuple[Block, Peer] = await self.__blockAndPeerQueue.get()
            if not blockAndPeer:
                return

            blockWithoutData: Block = blockAndPeer[0]
            requester: Peer = blockAndPeer[1]
            if blockWithoutData in requester.blocksRequestedByPeer:  # ensure the peer didn't cancel the request since first making it
                await PieceMessage(blockWithoutData.pieceIndex, blockWithoutData.beginOffset, self.__getBlockDataFromDisk(blockWithoutData)).send(requester)
                requester.blocksRequestedByPeer.remove(blockWithoutData)
