import tkinter
from tkinter import Tk, YES, BOTH, Menu
from tkinter.ttk import Treeview
from typing import List, Final, Literal
import utils
from service.processSingleTorrent import ProcessSingleTorrent
from service.sessionMetrics import SessionMetrics


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

    def __getSingleTorrentProcessorByTorrentName(self, torrentName: str) -> ProcessSingleTorrent:
        for singleTorrentProcessor in self.__singleTorrentProcessors:
            if singleTorrentProcessor.sessionMetrics.torrentName == torrentName:
                return singleTorrentProcessor

    def __pauseDownloadCommand(self, rowID: str) -> None:
        print(f"Paused the download of {rowID}")
        self.__getSingleTorrentProcessorByTorrentName(rowID).pauseDownload()

    def __resumeDownloadCommand(self, rowID: str) -> None:
        print(f"Resumed the download of {rowID}")
        self.__getSingleTorrentProcessorByTorrentName(rowID).resumeDownload()

    def __pauseUploadCommand(self, rowID: str) -> None:
        print(f"Paused the uploade of {rowID}")

    def __resumeUploadCommand(self, rowID: str) -> None:
        print(f"Resumed the upload of {rowID}")

    def __getCommandPauseDownloadStateFromRowID(self, rowID: str, commandLabel: str) -> Literal["normal", "disabled"]:
        singleTorrentProcessor: ProcessSingleTorrent = self.__getSingleTorrentProcessorByTorrentName(rowID)

        if (commandLabel == "Pause download" and singleTorrentProcessor.isDownloadPaused) or \
                (commandLabel == "Resume download" and not singleTorrentProcessor.isDownloadPaused):
            return "disabled"
        return "normal"

    def __displayContextMenuForRowID(self, rowID: str, eventXRoot: int, eventYRoot: int) -> None:
        menu: Menu = Menu(self.__treeView, tearoff=0)
        menu.add_command(label="Pause download",
                         command=lambda: self.__pauseDownloadCommand(rowID),
                         state=self.__getCommandPauseDownloadStateFromRowID(rowID, "Pause download"))
        menu.add_command(label="Resume download",
                         command=lambda: self.__resumeDownloadCommand(rowID),
                         state=self.__getCommandPauseDownloadStateFromRowID(rowID, "Resume download"))
        menu.add_command(label="Pause upload",
                         command=lambda: self.__pauseUploadCommand(rowID))
        menu.add_command(label="Resume upload",
                         command=lambda: self.__resumeUploadCommand(rowID),
                         state="disabled")
        menu.add_separator()
        menu.add_command(label="Open")
        menu.add_command(label="Open folder")
        menu.post(eventXRoot, eventYRoot)

    def __rightClickAction(self, event) -> None:
        rowID: str = self.__treeView.identify("item", event.x, event.y)
        if not rowID:
            return
        self.__treeView.selection_set(rowID)
        self.__treeView.focus_set()
        self.__treeView.focus(rowID)
        self.__displayContextMenuForRowID(rowID, event.x_root, event.y_root)

    def __createTreeView(self) -> Treeview:
        CENTER_ANCHOR: Final[str] = "center"
        MIN_COLUMN_WIDTH_IN_PIXELS: Final[int] = 130
        MAX_TORRENT_NAME_LENGTH: Final[int] = 100

        treeView: Treeview = Treeview(self.__mainWindow, columns=self.COLUMN_NAMES)
        for columnName in self.COLUMN_NAMES:
            treeView.heading(columnName, text=columnName, anchor=CENTER_ANCHOR)
            treeView.column(columnName, minwidth=MIN_COLUMN_WIDTH_IN_PIXELS, anchor=CENTER_ANCHOR)
        for sessionMetrics in self.__getSessionMetrics():
            treeView.insert("", tkinter.END, sessionMetrics.torrentName,
                            text=sessionMetrics.torrentName[: MAX_TORRENT_NAME_LENGTH],  # TODO - change the min width of this column
                            values=self.__getValuesFromSessionMetrics(sessionMetrics, self.COLUMN_NAMES))
        treeView.pack(expand=YES, fill=BOTH)
        treeView.bind("<3>", self.__rightClickAction)
        return treeView

    def refreshModel(self):
        for sessionMetrics in self.__getSessionMetrics():
            self.__treeView.item(sessionMetrics.torrentName, values=self.__getValuesFromSessionMetrics(sessionMetrics, self.COLUMN_NAMES))

    @property
    def treeView(self) -> Treeview:
        return self.__treeView
