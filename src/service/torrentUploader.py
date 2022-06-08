import asyncio
from asyncio import Task
from typing import Tuple
from domain.block import Block
from domain.message.pieceMessage import PieceMessage
from domain.peer import Peer
from service.torrentDiskLoader import TorrentDiskLoader
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class TorrentUploader:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__scanner: TorrentMetaInfoScanner = scanner
        self.__torrentDiskLoader: TorrentDiskLoader = TorrentDiskLoader(scanner)
        self.__blockAndPeerQueue: asyncio.Queue[Tuple[Block, Peer]]
        self.__running: bool = False

    def start(self) -> None:
        self.__running = True
        self.__blockAndPeerQueue = asyncio.Queue()
        task: Task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    """This can be called even if the uploader was not started yet"""
    def stop(self) -> None:
        self.__running = False

    def putBlockInQueue(self, blockWithoutData: Block, requester: Peer) -> None:
        self.__blockAndPeerQueue.put_nowait((blockWithoutData, requester))

    async def __run(self) -> None:
        while self.__running:
            blockAndPeer: Tuple[Block, Peer] = await self.__blockAndPeerQueue.get()
            if not blockAndPeer:
                return

            blockWithoutData: Block = blockAndPeer[0]
            requester: Peer = blockAndPeer[1]
            if blockWithoutData in requester.blocksRequestedByPeer:  # ensure the peer didn't cancel the request since first making it
                await PieceMessage(blockWithoutData.pieceIndex, blockWithoutData.beginOffset, self.__torrentDiskLoader.getDataForBlock(blockWithoutData)).send(requester)
                requester.blocksRequestedByPeer.remove(blockWithoutData)
