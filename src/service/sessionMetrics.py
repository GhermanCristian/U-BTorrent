import utils
from service.timeMetrics import TimeMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class SessionMetrics:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__totalDownloadedBytes: int = 0
        self.__totalUploadedBytes: int = 0
        self.__torrentName: str = scanner.torrentName
        self.__totalSize: int = scanner.getTotalContentSize()
        self.__timeMetrics: TimeMetrics = TimeMetrics()

    def start(self) -> None:
        self.__timeMetrics.start()

    def addDownloadedBytes(self, increment: int) -> None:
        self.__totalDownloadedBytes += increment
        self.__timeMetrics.downloadedBytesLastInterval += increment

    def addUploadedBytes(self, increment: int) -> None:
        self.__totalUploadedBytes += increment
        self.__timeMetrics.uploadedBytesLastInterval += increment

    def stopTimer(self) -> None:
        self.__timeMetrics.stopTimer()

    @property
    def torrentName(self) -> str:
        return self.__torrentName

    @property
    def downloadSpeed(self) -> float:
        return self.__timeMetrics.downloadSpeed

    @property
    def uploadSpeed(self) -> float:
        return self.__timeMetrics.uploadSpeed

    @property
    def elapsedTime(self) -> int:
        return self.__timeMetrics.elapsedTime

    @property
    def totalDownloadedBytes(self) -> int:
        return self.__totalDownloadedBytes

    @property
    def totalUploadedBytes(self) -> int:
        return self.__totalUploadedBytes

    @property
    def seedRatio(self) -> float:
        if self.__totalDownloadedBytes == 0:
            return 0.0
        return self.__totalUploadedBytes / self.__totalDownloadedBytes

    @property
    def totalSize(self) -> int:
        return self.__totalSize

    @property
    def completionPercentage(self) -> float:
        return self.__totalDownloadedBytes / self.__totalSize * 100

    @property
    def remainingBytes(self) -> int:
        return self.__totalSize - self.__totalDownloadedBytes

    @property
    def ETA(self) -> int:
        if self.downloadSpeed == 0:
            return utils.INFINITY
        return self.remainingBytes // int(self.downloadSpeed)
