import tkinter
from tkinter import *
from tkinter.ttk import Treeview
from typing import Final, List
import utils
from service.sessionMetrics import SessionMetrics
from service.torrentClient import TorrentClient


class GUI:
    COMPLETED_RATIO_COLUMN_NAME: Final[str] = "Completed"
    TOTAL_SIZE_COLUMN_NAME: Final[str] = "Size"
    REMAINING_SIZE_COLUMN_NAME: Final[str] = "Remaining"
    DOWNLOAD_SPEED_COLUMN_NAME: Final[str] = "Download speed"
    ETA_COLUMN_NAME: Final[str] = "ETA"
    ELAPSED_TIME_COLUMN_NAME: Final[str] = "Elapsed time"
    COLUMN_NAMES: Final[List[str]] = [COMPLETED_RATIO_COLUMN_NAME,
                                      REMAINING_SIZE_COLUMN_NAME,
                                      TOTAL_SIZE_COLUMN_NAME,
                                      DOWNLOAD_SPEED_COLUMN_NAME,
                                      ETA_COLUMN_NAME,
                                      ELAPSED_TIME_COLUMN_NAME]

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

    def __getValuesFromSessionMetrics(self, sessionMetrics: SessionMetrics, currentColumns: List[str]) -> List[str | int]:
        sessionMetricsValues: List[str | int] = []
        if self.COMPLETED_RATIO_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(f"{sessionMetrics.completionPercentage:.2f}%")
        if self.REMAINING_SIZE_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(utils.prettyPrintSize(sessionMetrics.remainingBytes))
        if self.TOTAL_SIZE_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(utils.prettyPrintSize(sessionMetrics.totalSize))
        if self.DOWNLOAD_SPEED_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(f"{utils.prettyPrintSize(sessionMetrics.downloadSpeed)}/s")
        if self.ETA_COLUMN_NAME in currentColumns:
            if sessionMetrics.ETA == utils.INFINITY or sessionMetrics.ETA == 0:
                sessionMetricsValues.append("-")
            else:
                sessionMetricsValues.append(f"{utils.prettyPrintTime(sessionMetrics.ETA)}")
        if self.ELAPSED_TIME_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(f"{utils.prettyPrintTime(sessionMetrics.elapsedTime)}")
        return sessionMetricsValues

    def __createTreeView(self) -> Treeview:
        CENTER_ANCHOR: Final[str] = "center"
        MIN_COLUMN_WIDTH_IN_PIXELS: Final[int] = 130
        
        treeView: Treeview = Treeview(self.__mainWindow, columns=self.COLUMN_NAMES)
        for columnName in self.COLUMN_NAMES:
            treeView.heading(columnName, text=columnName, anchor=CENTER_ANCHOR)
            treeView.column(columnName, minwidth=MIN_COLUMN_WIDTH_IN_PIXELS, anchor=CENTER_ANCHOR)
        for sessionMetrics in self.__getSessionMetrics():
            treeView.insert("", tkinter.END, sessionMetrics.torrentName,
                            text=sessionMetrics.torrentName,  # TODO - change the min width of this column
                            values=self.__getValuesFromSessionMetrics(sessionMetrics, self.COLUMN_NAMES))
        treeView.pack(expand=YES, fill=BOTH)
        return treeView

    def run(self) -> None:
        self.__refreshModel()
        self.__mainWindow.mainloop()

    def __refreshModel(self) -> None:
        REFRESH_INTERVAL_IN_MILLISECONDS: Final[int] = 1000

        for sessionMetrics in self.__getSessionMetrics():
            self.__treeView.item(sessionMetrics.torrentName, values=self.__getValuesFromSessionMetrics(sessionMetrics, self.COLUMN_NAMES))
        self.__mainWindow.after(REFRESH_INTERVAL_IN_MILLISECONDS, self.__refreshModel)
