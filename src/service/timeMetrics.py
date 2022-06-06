import asyncio
from asyncio import Task
from typing import Final


class TimeMetrics:
    SLEEP_INTERVAL_IN_SECONDS: Final[int] = 1

    def __init__(self):
        self.__downloading: bool = True
        self.__uploading: bool = True
        self.__elapsedTime: int = 0  # in seconds
        self.__downloadedBytesLastInterval: int = 0
        self.__uploadedBytesLastInterval: int = 0
        self.__downloadSpeed: float = 0.0  # bytes per second
        self.__uploadSpeed: float = 0.0  # bytes per second

    def start(self) -> None:
        task: Task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    def stopTimer(self) -> None:
        self.__downloading = False
        self.__uploading = False

    def setDownloadComplete(self) -> None:
        self.__downloading = False

    def setUploadStarted(self) -> None:
        self.__downloadSpeed = 0.0
        self.__uploading = True

    @property
    def downloadSpeed(self) -> float:
        return self.__downloadSpeed

    @property
    def uploadSpeed(self) -> float:
        return self.__uploadSpeed

    @property
    def elapsedTime(self) -> int:
        return self.__elapsedTime

    @property
    def downloadedBytesLastInterval(self) -> int:
        return self.__downloadedBytesLastInterval

    @downloadedBytesLastInterval.setter
    def downloadedBytesLastInterval(self, newValue: int) -> None:
        self.__downloadedBytesLastInterval = newValue

    @property
    def uploadedBytesLastInterval(self) -> int:
        return self.__uploadedBytesLastInterval

    @uploadedBytesLastInterval.setter
    def uploadedBytesLastInterval(self, newValue: int) -> None:
        self.__uploadedBytesLastInterval = newValue

    def __refreshDownloadValues(self) -> None:
        self.__elapsedTime += self.SLEEP_INTERVAL_IN_SECONDS
        self.__downloadSpeed = self.__downloadedBytesLastInterval / self.SLEEP_INTERVAL_IN_SECONDS
        self.__downloadedBytesLastInterval = 0

    def __refreshUploadValues(self) -> None:
        self.__elapsedTime += self.SLEEP_INTERVAL_IN_SECONDS
        self.__uploadSpeed = self.__uploadedBytesLastInterval / self.SLEEP_INTERVAL_IN_SECONDS
        print(self.__uploadSpeed)
        self.__uploadedBytesLastInterval = 0

    async def __run(self) -> None:
        while self.__downloading:
            await asyncio.sleep(self.SLEEP_INTERVAL_IN_SECONDS)
            self.__refreshDownloadValues()
        while self.__uploading:
            await asyncio.sleep(self.SLEEP_INTERVAL_IN_SECONDS)
            self.__refreshUploadValues()
