from concurrent.futures import ThreadPoolExecutor
from typing import List
from service.processSingleTorrent import ProcessSingleTorrent


class TorrentClient:
    def __init__(self):
        self.__torrentFilePathList: List[str] = ["..\\Resources\\medical.torrent",
                                                 "..\\Resources\\mars.torrent",
                                                 "..\\Resources\\ppcoin.torrent"]

    def __torrentProcessorWrapper(self, torrentFilePath: str) -> None:
        ProcessSingleTorrent(torrentFilePath)

    def start(self) -> None:
        with ThreadPoolExecutor(len(self.__torrentFilePathList)) as executor:
            for path in self.__torrentFilePathList:
                executor.submit(self.__torrentProcessorWrapper, path)
