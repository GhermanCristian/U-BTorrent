import utils
from service.timeMetrics import TimeMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class SessionMetrics:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__totalCompletedBytes: int = 0
        self.__totalSize: int = scanner.getTotalContentSize()
        self.__timeMetrics: TimeMetrics = TimeMetrics()

    def addCompletedBytes(self, increment: int) -> None:
        self.__totalCompletedBytes += increment
        self.__timeMetrics.downloadedBytesLastInterval += increment
        self.__refreshMetrics()

    # TODO - add another timer here which takes care of the refresh rate in the GUI; perhaps with a customizable interval
    # currently the data is refreshed after each block arrives (in addCompletedBytes) - which is way too often
    # this timer will be different than the one which computes the download speed & stuff
    def __refreshMetrics(self) -> None:
        print(f"Elapsed time: {self.__timeMetrics.elapsedTime} s")
        print(f"{utils.prettyPrintSize(self.__timeMetrics.downloadSpeed)}/s")
        print(f"{self.completionPercentage:.2f}%")

    def stopTimer(self) -> None:
        self.__timeMetrics.stopTimer()

    @property
    def totalCompletedBytes(self) -> int:
        return self.__totalCompletedBytes

    @property
    def totalSize(self) -> int:
        return self.__totalSize

    @property
    def completionPercentage(self) -> float:
        return self.__totalCompletedBytes / self.__totalSize * 100
