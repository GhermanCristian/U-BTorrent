import tkinter
from tkinter import Tk, YES, BOTH
from tkinter.ttk import Treeview, Style
from typing import List, Final
import utils
from service.processSingleTorrent import ProcessSingleTorrent
from service.sessionMetrics import SessionMetrics
from ui.contextMenuLogic import ContextMenuLogic


class TreeViewLogic:
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

    def __init__(self, mainWindow: Tk, singleTorrentProcessors: List[ProcessSingleTorrent]):
        self.__mainWindow: Tk = mainWindow
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = singleTorrentProcessors
        self.__treeView: Treeview = self.__createTreeView()
        self.__contextMenuLogic: ContextMenuLogic = ContextMenuLogic(self.__treeView, singleTorrentProcessors)

    def __getValuesFromSessionMetrics(self, sessionMetrics: SessionMetrics, currentColumns: List[str]) -> List[str | int]:
        sessionMetricsValues: List[str | int] = []
        if self.COMPLETED_RATIO_COLUMN_NAME in currentColumns:
            # TODO - make this a progress bar
            sessionMetricsValues.append(f"{sessionMetrics.completionPercentage:.2f}%")
        if self.REMAINING_SIZE_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(utils.prettyPrintSize(sessionMetrics.remainingBytes))
        if self.TOTAL_SIZE_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(utils.prettyPrintSize(sessionMetrics.totalSize))
        if self.DOWNLOAD_SPEED_COLUMN_NAME in currentColumns:
            if sessionMetrics.downloadSpeed == 0:
                sessionMetricsValues.append("-")
            else:
                sessionMetricsValues.append(f"{utils.prettyPrintSize(sessionMetrics.downloadSpeed)}/s")
        if self.ETA_COLUMN_NAME in currentColumns:
            if sessionMetrics.ETA == utils.INFINITY:
                sessionMetricsValues.append("∞")
            elif sessionMetrics.ETA == 0:
                sessionMetricsValues.append("-")
            else:
                sessionMetricsValues.append(f"{utils.prettyPrintTime(sessionMetrics.ETA)}")
        if self.ELAPSED_TIME_COLUMN_NAME in currentColumns:
            sessionMetricsValues.append(f"{utils.prettyPrintTime(sessionMetrics.elapsedTime)}")
        return sessionMetricsValues

    def __getSessionMetrics(self) -> List[SessionMetrics]:
        return [singleTorrentProcessor.sessionMetrics for singleTorrentProcessor in self.__singleTorrentProcessors]

    def __rightClickAction(self, event) -> None:
        rowID: str = self.__treeView.identify("item", event.x, event.y)
        if not rowID:
            return
        self.__treeView.selection_set(rowID)
        self.__treeView.focus_set()
        self.__treeView.focus(rowID)
        self.__contextMenuLogic.displayContextMenuForRowID(rowID, event.x_root, event.y_root)

    def __applyStyle(self) -> None:
        TREEVIEW_HEADING_FONT_SIZE: Final[int] = 11
        TREEVIEW_HEADING_IDENTIFIER: Final[str] = "Treeview.Heading"
        TREEVIEW_CONTENT_FONT_SIZE: Final[int] = 10
        TREEVIEW_CONTENT_IDENTIFIER: Final[str] = "Treeview"

        style = Style()
        style.configure(TREEVIEW_HEADING_IDENTIFIER, font=(None, TREEVIEW_HEADING_FONT_SIZE))
        style.configure(TREEVIEW_CONTENT_IDENTIFIER, font=(None, TREEVIEW_CONTENT_FONT_SIZE))

    def __createTreeView(self) -> Treeview:
        CENTER_ANCHOR: Final[str] = "center"
        MIN_COLUMN_WIDTH_IN_PIXELS: Final[int] = 100
        MIN_WIDTH_NAME_COLUMN_IN_PIXELS: Final[int] = 200
        NAME_COLUMN_IDENTIFIER: Final[str] = "#0"
        MAX_TORRENT_NAME_LENGTH: Final[int] = 100
        RIGHT_CLICK_IDENTIFIER: Final[str] = "<3>"

        treeView: Treeview = Treeview(self.__mainWindow, columns=self.COLUMN_NAMES)
        self.__applyStyle()
        treeView.column(NAME_COLUMN_IDENTIFIER, minwidth=MIN_WIDTH_NAME_COLUMN_IN_PIXELS)
        for columnName in self.COLUMN_NAMES:
            treeView.heading(columnName, text=columnName, anchor=CENTER_ANCHOR)
            treeView.column(columnName, minwidth=MIN_COLUMN_WIDTH_IN_PIXELS, anchor=CENTER_ANCHOR)
        for sessionMetrics in self.__getSessionMetrics():
            treeView.insert("", tkinter.END, sessionMetrics.torrentName,
                            text=sessionMetrics.torrentName[: MAX_TORRENT_NAME_LENGTH],
                            values=self.__getValuesFromSessionMetrics(sessionMetrics, self.COLUMN_NAMES))
        treeView.pack(expand=YES, fill=BOTH)
        treeView.bind(RIGHT_CLICK_IDENTIFIER, self.__rightClickAction)
        return treeView

    def refreshModel(self):
        for sessionMetrics in self.__getSessionMetrics():
            self.__treeView.item(sessionMetrics.torrentName, values=self.__getValuesFromSessionMetrics(sessionMetrics, self.COLUMN_NAMES))

    @property
    def treeView(self) -> Treeview:
        return self.__treeView
