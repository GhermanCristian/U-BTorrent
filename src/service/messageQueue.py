import asyncio
from asyncio import Task
from typing import Tuple
from domain.message.message import Message
from domain.peer import Peer
from service.downloadSession import DownloadSession
from service.messageProcessor import MessageProcessor


class MessageQueue:
    def __init__(self, downloadSession: DownloadSession):
        self.__downloadSession: DownloadSession = downloadSession
        self.__messagesQueue: asyncio.Queue[Tuple[Message, Peer]] = asyncio.Queue()
        self.__running: bool = True

    def start(self) -> None:
        task: Task = asyncio.create_task(self.__run())  # store the var reference to avoid the task disappearing mid-execution

    async def __run(self) -> None:
        while self.__running:
            messageAndPeer: Tuple[Message, Peer] = await self.__messagesQueue.get()
            if not messageAndPeer:
                return
            await MessageProcessor(messageAndPeer[1], self.__downloadSession).processMessage(messageAndPeer[0])

    @property
    def running(self) -> bool:
        return self.__running

    @running.setter
    def running(self, newValue: bool) -> None:
        self.__running = newValue

    def putMessageInQueue(self, message: Message, sender: Peer) -> None:
        self.__messagesQueue.put_nowait((message, sender))
