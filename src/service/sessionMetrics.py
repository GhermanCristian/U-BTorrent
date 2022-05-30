from service.timeMetrics import TimeMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class SessionMetrics:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__totalCompletedBytes: int = 0
        self.__totalSize: int = scanner.getTotalContentSize()
        self.__timeMetrics: TimeMetrics = TimeMetrics()

    def start(self) -> None:
        self.__timeMetrics.start()

    def addCompletedBytes(self, increment: int) -> None:
        self.__totalCompletedBytes += increment
        self.__timeMetrics.downloadedBytesLastInterval += increment

    def stopTimer(self) -> None:
        self.__timeMetrics.stopTimer()

    @property
    def downloadSpeed(self) -> float:
        return self.__timeMetrics.downloadSpeed

    @property
    def elapsedTime(self) -> int:
        return self.__timeMetrics.elapsedTime

    @property
    def totalCompletedBytes(self) -> int:
        return self.__totalCompletedBytes

    @property
    def totalSize(self) -> int:
        return self.__totalSize

    @property
    def completionPercentage(self) -> float:
        return self.__totalCompletedBytes / self.__totalSize * 100
