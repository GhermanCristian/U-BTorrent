import asyncio
from asyncio import Task
from typing import Final
import utils
from service.timeMetrics import TimeMetrics
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner


class SessionMetrics:
    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__totalCompletedBytes: int = 0
        self.__totalSize: int = scanner.getTotalContentSize()
        self.__timeMetrics: TimeMetrics = TimeMetrics()
        self.__task: Task = asyncio.create_task(self.__refreshTimer())  # store the var reference to avoid the task disappearing mid-execution
        self.__refreshTimerRunning: bool = True

    def addCompletedBytes(self, increment: int) -> None:
        self.__totalCompletedBytes += increment
        self.__timeMetrics.downloadedBytesLastInterval += increment
        
    async def __refreshTimer(self) -> None:
        REFRESH_INTERVAL_IN_SECONDS: Final[float] = 2  # will be customizable when implementing the GUI
        
        while self.__refreshTimerRunning:
            await asyncio.sleep(REFRESH_INTERVAL_IN_SECONDS)
            self.__refreshMetrics()

    def __refreshMetrics(self) -> None:
        # this method will just send data to the GUI (the "update" in the Observer pattern)
        print(f"Elapsed time: {self.__timeMetrics.elapsedTime} s")
        print(f"{utils.prettyPrintSize(self.__timeMetrics.downloadSpeed)}/s")
        print(f"{self.completionPercentage:.2f}%")

    def stopAllTimers(self) -> None:
        self.__refreshTimerRunning = False
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
