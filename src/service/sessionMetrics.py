import utils
from service.timeMetrics import TimeMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class SessionMetrics:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__totalCompletedBytes: int = 0
        self.__torrentName: str = scanner.torrentName
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
    def torrentName(self) -> str:
        return self.__torrentName

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

    @property
    def remainingBytes(self) -> int:
        return self.__totalSize - self.__totalCompletedBytes

    @property
    def ETA(self) -> int:
        if self.downloadSpeed == 0:
            return utils.INFINITY
        return self.remainingBytes // int(self.downloadSpeed)
