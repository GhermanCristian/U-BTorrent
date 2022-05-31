from tkinter.ttk import Treeview
from typing import List, Literal
from tkinter import Menu
from service.processSingleTorrent import ProcessSingleTorrent


class ContextMenuLogic:
    def __init__(self, treeView: Treeview, singleTorrentProcessors: List[ProcessSingleTorrent]):
        self.__treeView: Treeview = treeView
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = singleTorrentProcessors

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
        print(f"Paused the upload of {rowID}")

    def __resumeUploadCommand(self, rowID: str) -> None:
        print(f"Resumed the upload of {rowID}")

    def __getCommandPauseDownloadStateFromRowID(self, rowID: str, commandLabel: str) -> Literal["normal", "disabled"]:
        singleTorrentProcessor: ProcessSingleTorrent = self.__getSingleTorrentProcessorByTorrentName(rowID)

        if (commandLabel == "Pause download" and singleTorrentProcessor.isDownloadPaused) or \
                (commandLabel == "Resume download" and not singleTorrentProcessor.isDownloadPaused):
            return "disabled"
        return "normal"

    def displayContextMenuForRowID(self, rowID: str, eventXRoot: int, eventYRoot: int) -> None:
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
