from tkinter import *
from tkinter import ttk
from typing import Final
from service.torrentClient import TorrentClient


class GUI:
    WINDOW_TITLE: Final[str] = "Torrent client"
    MIN_WINDOW_WIDTH_IN_PIXELS: Final[int] = 640
    MIN_WINDOW_HEIGHT_IN_PIXELS: Final[int] = 480

    def __init__(self, torrentClient: TorrentClient):
        self.__torrentClient: TorrentClient = torrentClient

        self.__mainWindow: Tk = Tk()
        self.__mainWindow.title(self.WINDOW_TITLE)
        self.__mainWindow.minsize(self.MIN_WINDOW_WIDTH_IN_PIXELS, self.MIN_WINDOW_HEIGHT_IN_PIXELS)
        self.__frame = ttk.Frame(self.__mainWindow, padding=10)
        self.__frame.grid()
        self.__label = ttk.Label(self.__frame, text="some text")
        self.__label.grid(column=0, row=0)

    def run(self) -> None:
        ttk.Button(self.__frame, text="Quit", command=self.__mainWindow.destroy).grid(column=1, row=0)
        self.__refreshModel()
        self.__mainWindow.mainloop()

    def __refreshModel(self) -> None:
        [print(singleTorrentProcessor.sessionMetrics.completionPercentage) for singleTorrentProcessor in self.__torrentClient.singleTorrentProcessors]
        self.__mainWindow.after(1000, self.__refreshModel)
