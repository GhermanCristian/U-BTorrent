import tkinter
from tkinter import Tk, YES, BOTH
from tkinter.ttk import Treeview, Style
from typing import List, Final, Tuple, Dict
import utils
from service.processSingleTorrent import ProcessSingleTorrent
from service.sessionMetrics import SessionMetrics
from ui import utilsGUI
from ui.contextMenu import ContextMenu


class TorrentList:
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
        self.__contextMenuLogic: ContextMenu = ContextMenu(self.__treeView, singleTorrentProcessors)

    def __getDownloadSpeedInViewForm(self, downloadSpeed: float) -> str:
        if downloadSpeed == 0:
            return "-"
        return f"{utils.prettyPrintSize(downloadSpeed)}/s"

    def __getETAInViewForm(self, ETA: int) -> str:
        if ETA == utils.INFINITY:
            return "∞"
        if ETA == 0:
            return "-"
        return f"{utils.prettyPrintTime(ETA)}"

    def __getValuesFromSessionMetricsInViewForm(self, sessionMetrics: SessionMetrics, currentColumns: List[str]) -> List[str]:
        # TODO - transform the completed ratio column into a progress bar
        IDENTIFIER_TO_VIEW_FORM: Dict[str, str] = {
            self.COMPLETED_RATIO_COLUMN_NAME: f"{sessionMetrics.completionPercentage:.2f}%",
            self.REMAINING_SIZE_COLUMN_NAME: utils.prettyPrintSize(sessionMetrics.remainingBytes),
            self.TOTAL_SIZE_COLUMN_NAME: utils.prettyPrintSize(sessionMetrics.totalSize),
            self.DOWNLOAD_SPEED_COLUMN_NAME: self.__getDownloadSpeedInViewForm(sessionMetrics.downloadSpeed),
            self.ETA_COLUMN_NAME: self.__getETAInViewForm(sessionMetrics.ETA),
            self.ELAPSED_TIME_COLUMN_NAME: f"{utils.prettyPrintTime(sessionMetrics.elapsedTime)}"
        }
        return [IDENTIFIER_TO_VIEW_FORM[columnIdentifier] for columnIdentifier in currentColumns]

    def __getSessionMetrics(self) -> List[SessionMetrics]:
        return [singleTorrentProcessor.sessionMetrics for singleTorrentProcessor in self.__singleTorrentProcessors]

    def __getValueFromSessionMetrics(self, sessionMetrics: SessionMetrics, columnIdentifier: str) -> int | float:
        IDENTIFIER_TO_FIELD: Final[Dict[str, int | float]] = {
            self.COMPLETED_RATIO_COLUMN_NAME: sessionMetrics.completionPercentage,
            self.REMAINING_SIZE_COLUMN_NAME: sessionMetrics.remainingBytes,
            self.TOTAL_SIZE_COLUMN_NAME: sessionMetrics.totalSize,
            self.DOWNLOAD_SPEED_COLUMN_NAME: sessionMetrics.downloadSpeed,
            self.ETA_COLUMN_NAME: sessionMetrics.ETA,
            self.ELAPSED_TIME_COLUMN_NAME: sessionMetrics.elapsedTime
        }
        return IDENTIFIER_TO_FIELD[columnIdentifier]

    def __getValuesAndRowNamesForColumn(self, columnName: str) -> List[Tuple[int | float, str]]:
        # torrent name = row name
        return [(self.__getValueFromSessionMetrics(sessionMetrics, columnName), sessionMetrics.torrentName) for sessionMetrics in self.__getSessionMetrics()]

    def __sortColumn(self, treeView: Treeview, columnName: str, reverse: bool) -> None:
        ROOT_PARENT: Final[str] = ""

        valuesWithRowNames: List[Tuple[int | float, str]] = self.__getValuesAndRowNamesForColumn(columnName)
        valuesWithRowNames.sort(reverse=reverse)
        for index, (val, item) in enumerate(valuesWithRowNames):
            treeView.move(item, ROOT_PARENT, index)
        # next time this column is clicked, perform the inverse of the current operation
        treeView.heading(columnName,
                         text=columnName,
                         command=lambda colName=columnName: self.__sortColumn(treeView, colName, not reverse))

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

        style: Style = Style()
        style.configure(TREEVIEW_HEADING_IDENTIFIER,
                        font=(utilsGUI.FONT_NAME, TREEVIEW_HEADING_FONT_SIZE))
        style.configure(TREEVIEW_CONTENT_IDENTIFIER,
                        font=(utilsGUI.FONT_NAME, TREEVIEW_CONTENT_FONT_SIZE))

    def __addColumns(self, treeView: Treeview) -> None:
        CENTER_ANCHOR: Final[str] = "center"
        MIN_COLUMN_WIDTH_IN_PIXELS: Final[int] = 100
        MIN_WIDTH_NAME_COLUMN_IN_PIXELS: Final[int] = 200
        NAME_COLUMN_IDENTIFIER: Final[str] = "#0"
        MAX_TORRENT_NAME_LENGTH: Final[int] = 100

        treeView.column(NAME_COLUMN_IDENTIFIER,
                        minwidth=MIN_WIDTH_NAME_COLUMN_IN_PIXELS)
        for columnName in self.COLUMN_NAMES:
            # TODO - also sort the name column
            treeView.heading(columnName,
                             text=columnName,
                             anchor=CENTER_ANCHOR,
                             command=lambda colName=columnName: self.__sortColumn(treeView, colName, False))
            treeView.column(columnName,
                            minwidth=MIN_COLUMN_WIDTH_IN_PIXELS,
                            anchor=CENTER_ANCHOR)
        for sessionMetrics in self.__getSessionMetrics():
            treeView.insert("", tkinter.END, sessionMetrics.torrentName,
                            text=sessionMetrics.torrentName[: MAX_TORRENT_NAME_LENGTH],
                            values=self.__getValuesFromSessionMetricsInViewForm(sessionMetrics, self.COLUMN_NAMES))

    def __createTreeView(self) -> Treeview:
        RIGHT_CLICK_IDENTIFIER: Final[str] = "<3>"

        treeView: Treeview = Treeview(self.__mainWindow,
                                      columns=self.COLUMN_NAMES)
        self.__applyStyle()
        self.__addColumns(treeView)
        treeView.pack(expand=YES,
                      fill=BOTH)
        treeView.bind(RIGHT_CLICK_IDENTIFIER, self.__rightClickAction)
        return treeView

    def refreshModel(self):
        for sessionMetrics in self.__getSessionMetrics():
            self.__treeView.item(sessionMetrics.torrentName,
                                 values=self.__getValuesFromSessionMetricsInViewForm(sessionMetrics, self.COLUMN_NAMES))

    @property
    def treeView(self) -> Treeview:
        return self.__treeView
