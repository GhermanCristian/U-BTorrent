from tkinter.ttk import Treeview
from typing import List, Literal, Final
from tkinter import Menu
from service.processSingleTorrent import ProcessSingleTorrent
from ui import utilsGUI


class ContextMenu:
    PAUSE_DOWNLOAD_COMMAND_LABEL: Final[str] = "Pause download"
    RESUME_DOWNLOAD_COMMAND_LABEL: Final[str] = "Resume download"
    PAUSE_UPLOAD_COMMAND_LABEL: Final[str] = "Pause upload"
    RESUME_UPLOAD_COMMAND_LABEL: Final[str] = "Resume upload"
    OPEN_COMMAND_LABEL: Final[str] = "Open"
    OPEN_FOLDER_COMMAND_LABEL: Final[str] = "Open folder"

    NORMAL_COMMAND_STATE: Final[Literal["normal"]] = "normal"
    DISABLED_COMMAND_STATE: Final[Literal["disabled"]] = "disabled"

    def __init__(self, treeView: Treeview, singleTorrentProcessors: List[ProcessSingleTorrent]):
        self.__treeView: Treeview = treeView
        self.__singleTorrentProcessors: List[ProcessSingleTorrent] = singleTorrentProcessors

    def __getSingleTorrentProcessorByTorrentName(self, torrentName: str) -> ProcessSingleTorrent:
        for singleTorrentProcessor in self.__singleTorrentProcessors:
            if singleTorrentProcessor.sessionMetrics.torrentName == torrentName:
                return singleTorrentProcessor

    def __pauseDownloadCommand(self, rowID: str) -> None:
        self.__getSingleTorrentProcessorByTorrentName(rowID).pauseDownload()

    def __resumeDownloadCommand(self, rowID: str) -> None:
        self.__getSingleTorrentProcessorByTorrentName(rowID).resumeDownload()

    def __pauseUploadCommand(self, rowID: str) -> None:
        self.__getSingleTorrentProcessorByTorrentName(rowID).pauseUpload()

    def __resumeUploadCommand(self, rowID: str) -> None:
        self.__getSingleTorrentProcessorByTorrentName(rowID).resumeUpload()

    def __getCommandPauseDownloadStateFromRowID(self, rowID: str, commandLabel: str) -> Literal["normal", "disabled"]:
        singleTorrentProcessor: ProcessSingleTorrent = self.__getSingleTorrentProcessorByTorrentName(rowID)

        if singleTorrentProcessor.isDownloaded or \
            (commandLabel == self.PAUSE_DOWNLOAD_COMMAND_LABEL and singleTorrentProcessor.isDownloadPaused) or \
                (commandLabel == self.RESUME_DOWNLOAD_COMMAND_LABEL and not singleTorrentProcessor.isDownloadPaused):
            return self.DISABLED_COMMAND_STATE
        return self.NORMAL_COMMAND_STATE

    def __getCommandPauseUploadStateFromRowID(self, rowID: str, commandLabel: str) -> Literal["normal", "disabled"]:
        singleTorrentProcessor: ProcessSingleTorrent = self.__getSingleTorrentProcessorByTorrentName(rowID)

        if not singleTorrentProcessor.isDownloaded or \
            (commandLabel == self.PAUSE_UPLOAD_COMMAND_LABEL and singleTorrentProcessor.isUploadPaused) or \
                (commandLabel == self.RESUME_UPLOAD_COMMAND_LABEL and not singleTorrentProcessor.isUploadPaused):
            return self.DISABLED_COMMAND_STATE
        return self.NORMAL_COMMAND_STATE

    def displayContextMenuForRowID(self, rowID: str, eventXRoot: int, eventYRoot: int) -> None:
        menu: Menu = Menu(self.__treeView, tearoff=utilsGUI.NO_MENU_TEAROFF)
        menu.add_command(label=self.PAUSE_DOWNLOAD_COMMAND_LABEL,
                         command=lambda: self.__pauseDownloadCommand(rowID),
                         state=self.__getCommandPauseDownloadStateFromRowID(rowID, self.PAUSE_DOWNLOAD_COMMAND_LABEL))
        menu.add_command(label=self.RESUME_DOWNLOAD_COMMAND_LABEL,
                         command=lambda: self.__resumeDownloadCommand(rowID),
                         state=self.__getCommandPauseDownloadStateFromRowID(rowID, self.RESUME_DOWNLOAD_COMMAND_LABEL))
        menu.add_command(label=self.PAUSE_UPLOAD_COMMAND_LABEL,
                         command=lambda: self.__pauseUploadCommand(rowID),
                         state=self.__getCommandPauseUploadStateFromRowID(rowID, self.PAUSE_UPLOAD_COMMAND_LABEL))
        menu.add_command(label=self.RESUME_UPLOAD_COMMAND_LABEL,
                         command=lambda: self.__resumeUploadCommand(rowID),
                         state=self.__getCommandPauseUploadStateFromRowID(rowID, self.RESUME_UPLOAD_COMMAND_LABEL))
        menu.add_separator()
        menu.add_command(label=self.OPEN_COMMAND_LABEL)
        menu.add_command(label=self.OPEN_FOLDER_COMMAND_LABEL)
        menu.post(eventXRoot, eventYRoot)
