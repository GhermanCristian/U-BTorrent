import tkinter
from tkinter import *
from tkinter.ttk import Treeview
from typing import Final, List, Tuple
import utils
from service.sessionMetrics import SessionMetrics
from service.torrentClient import TorrentClient


class GUI:
    def __init__(self, torrentClient: TorrentClient):
        self.__torrentClient: TorrentClient = torrentClient

        self.__mainWindow: Tk = self.__createMainWindow()
        self.__treeView: Treeview = self.__createTreeView()

    def __getSessionMetrics(self) -> List[SessionMetrics]:
        return [singleTorrentProcessor.sessionMetrics for singleTorrentProcessor in self.__torrentClient.singleTorrentProcessors]

    def __createMainWindow(self) -> Tk:
        WINDOW_TITLE: Final[str] = "Torrent client"
        MIN_WINDOW_WIDTH_IN_PIXELS: Final[int] = 640
        MIN_WINDOW_HEIGHT_IN_PIXELS: Final[int] = 480

        mainWindow: Tk = Tk()
        mainWindow.title(WINDOW_TITLE)
        mainWindow.minsize(MIN_WINDOW_WIDTH_IN_PIXELS, MIN_WINDOW_HEIGHT_IN_PIXELS)
        return mainWindow

    def __getValuesFromSessionMetrics(self, sessionMetrics: SessionMetrics) -> Tuple:
        return f"{sessionMetrics.completionPercentage:.2f}%", utils.prettyPrintSize(sessionMetrics.totalSize), utils.prettyPrintSize(sessionMetrics.downloadSpeed)

    def __createTreeView(self) -> Treeview:
        treeView: Treeview = Treeview(self.__mainWindow, columns=("Completed", "Total", "Download speed"))
        treeView.heading("Completed", text="Completed", anchor="center")
        treeView.column("Completed", minwidth=180, anchor="center")
        treeView.heading("Total", text="Total", anchor="center")
        treeView.column("Total", minwidth=180, anchor="center")
        treeView.heading("Download speed", text="Download speed", anchor="center")
        treeView.column("Download speed", minwidth=180, anchor="center")
        for sessionMetrics in self.__getSessionMetrics():
            treeView.insert("", tkinter.END, sessionMetrics.torrentName,
                            text=sessionMetrics.torrentName,  # TODO - change the min width of this
                            values=self.__getValuesFromSessionMetrics(sessionMetrics))
        treeView.pack(expand=YES, fill=BOTH)
        return treeView

    def run(self) -> None:
        self.__refreshModel()
        self.__mainWindow.mainloop()

    def __refreshModel(self) -> None:
        for sessionMetrics in self.__getSessionMetrics():
            self.__treeView.item(sessionMetrics.torrentName, values=self.__getValuesFromSessionMetrics(sessionMetrics))
        self.__mainWindow.after(1000, self.__refreshModel)
