from concurrent.futures import ThreadPoolExecutor
from typing import List, Final
from service.processSingleTorrent import ProcessSingleTorrent
from service.subject import Subject


class TorrentClient(Subject):
    def __init__(self):
        super().__init__()
        torrentFilePathList: Final[List[str]] = ["..\\Resources\\medical.torrent",
                                                 "..\\Resources\\mars.torrent",
                                                 "..\\Resources\\ppcoin.torrent"]
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = [ProcessSingleTorrent(path) for path in torrentFilePathList]

    def start(self) -> None:
        with ThreadPoolExecutor(len(self.__singleTorrentProcessors)) as executor:
            for singleTorrentProcessor in self.__singleTorrentProcessors:
                executor.submit(singleTorrentProcessor.run)

    @property
    def singleTorrentProcessors(self) -> List[ProcessSingleTorrent]:
        return self.__singleTorrentProcessors
