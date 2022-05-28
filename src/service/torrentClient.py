from concurrent.futures import ThreadPoolExecutor
from typing import List, Final
from service.processSingleTorrent import ProcessSingleTorrent


class TorrentClient:
    def __init__(self):
        torrentFilePathList: Final[List[str]] = ["..\\Resources\\medical.torrent",
                                                 "..\\Resources\\mars.torrent",
                                                 "..\\Resources\\ppcoin.torrent"]
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = [ProcessSingleTorrent(path) for path in torrentFilePathList]

    def start(self) -> None:
        with ThreadPoolExecutor(len(self.__singleTorrentProcessors)) as executor:
            for singleTorrentProcessor in self.__singleTorrentProcessors:
                executor.submit(singleTorrentProcessor.run)
