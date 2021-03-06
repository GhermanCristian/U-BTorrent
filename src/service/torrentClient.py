from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple
from service.processSingleTorrent import ProcessSingleTorrent


class TorrentClient:
    def __init__(self, torrentFilesPaths: Tuple[str, ...], downloadLocation: str):
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = [ProcessSingleTorrent(path, downloadLocation) for path in torrentFilesPaths]

    def start(self) -> None:
        with ThreadPoolExecutor(len(self.__singleTorrentProcessors)) as executor:
            for singleTorrentProcessor in self.__singleTorrentProcessors:
                executor.submit(singleTorrentProcessor.run)

    def stop(self) -> None:
        for singleTorrentProcessor in self.__singleTorrentProcessors:
            singleTorrentProcessor.stop()

    @property
    def singleTorrentProcessors(self) -> List[ProcessSingleTorrent]:
        return self.__singleTorrentProcessors
