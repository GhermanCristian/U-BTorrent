from tkinter import *
from tkinter import ttk
from typing import Final, List
from service.observer import Observer
from service.processSingleTorrent import ProcessSingleTorrent


class GUI(Observer):
    WINDOW_TITLE: Final[str] = "Torrent client"
    MIN_WINDOW_WIDTH_IN_PIXELS: Final[int] = 640
    MIN_WINDOW_HEIGHT_IN_PIXELS: Final[int] = 480

    def __init__(self, singleTorrentProcessors: List[ProcessSingleTorrent]):
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = singleTorrentProcessors

    def run(self) -> None:
        mainWindow: Tk = Tk()
        mainWindow.title(self.WINDOW_TITLE)
        mainWindow.minsize(self.MIN_WINDOW_WIDTH_IN_PIXELS, self.MIN_WINDOW_HEIGHT_IN_PIXELS)
        frame = ttk.Frame(mainWindow, padding=10)
        frame.grid()
        ttk.Label(frame, text="some text").grid(column=0, row=0)
        ttk.Button(frame, text="Quit", command=mainWindow.destroy).grid(column=1, row=0)
        mainWindow.mainloop()

    def update(self) -> None:
        # sth like "labelX.set text = singleTorrentProcessors[y].somevalue"
        pass
