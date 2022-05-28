import asyncio
from asyncio import Task
from typing import Final
import utils


class TimeMetrics:
    def __init__(self):
        self.__running: bool = True
        self.__elapsedTime: int = 0  # in seconds
        self.__downloadedBytesLastInterval: int = 0
        self.__task: Task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    def stopTimer(self) -> None:
        self.__running = False

    @property
    def elapsedTime(self) -> int:
        return self.__elapsedTime

    @property
    def downloadedBytesLastInterval(self) -> int:
        return self.__downloadedBytesLastInterval

    @downloadedBytesLastInterval.setter
    def downloadedBytesLastInterval(self, newValue: int) -> None:
        self.__downloadedBytesLastInterval = newValue

    async def __run(self) -> None:
        SLEEP_INTERVAL_IN_SECONDS: Final[int] = 1
        DOWNLOAD_SPEED_INTERVAL: Final[float] = 1.5

        while self.__running:
            await asyncio.sleep(SLEEP_INTERVAL_IN_SECONDS)
            self.__elapsedTime += SLEEP_INTERVAL_IN_SECONDS
            if self.__elapsedTime % DOWNLOAD_SPEED_INTERVAL == 0:
                print(f"{utils.prettyPrintSize(self.__downloadedBytesLastInterval / DOWNLOAD_SPEED_INTERVAL)}/s")
                self.__downloadedBytesLastInterval = 0
            print(self.__elapsedTime)
        print("finished")
