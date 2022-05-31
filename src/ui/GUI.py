import threading
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Treeview
from typing import Final, Tuple
from service.torrentClient import TorrentClient
from ui.treeViewLogic import TreeViewLogic


class GUI:
    INITIAL_DIRECTORY_PATH: Final[str] = "..\\Resources"

    def __init__(self):
        self.__mainWindow: Tk = self.__createMainWindow()
        
        torrentFilesPaths: Tuple[str, ...] = self.__selectTorrentFilesPaths()
        downloadLocation: str = self.__selectBaseDownloadLocation()  # this won't be prompted every time, rather it will be in a settings menu or sth
        # perhaps store it permanently in a config file or sth ?
        self.__torrentClient: TorrentClient = TorrentClient(torrentFilesPaths, downloadLocation)

        self.__treeViewLogic: TreeViewLogic = TreeViewLogic(self.__mainWindow, self.__torrentClient.singleTorrentProcessors)
        self.__treeView: Treeview = self.__treeViewLogic.treeView

    def __createMainWindow(self) -> Tk:
        WINDOW_TITLE: Final[str] = "Torrent client"
        MIN_WINDOW_WIDTH_IN_PIXELS: Final[int] = 640
        MIN_WINDOW_HEIGHT_IN_PIXELS: Final[int] = 480

        mainWindow: Tk = Tk()
        mainWindow.title(WINDOW_TITLE)
        mainWindow.minsize(MIN_WINDOW_WIDTH_IN_PIXELS, MIN_WINDOW_HEIGHT_IN_PIXELS)
        return mainWindow

    def __selectTorrentFilesPaths(self) -> Tuple[str, ...]:
        FILE_DIALOG_TITLE: Final[str] = "Select .torrent files"
        FILE_TYPE_DESCRIPTION: Final[str] = ".torrent files"
        DOT_TORRENT_FILE_PATTERN: Final[str] = "*.torrent"

        return filedialog.askopenfilenames(initialdir=self.INITIAL_DIRECTORY_PATH,
                                           title=FILE_DIALOG_TITLE,
                                           filetypes=((FILE_TYPE_DESCRIPTION, DOT_TORRENT_FILE_PATTERN),))

    def __selectBaseDownloadLocation(self) -> str:
        DOWNLOAD_LOCATION_DIALOG_TITLE: Final[str] = "Select the download location"
        return filedialog.askdirectory(initialdir=self.INITIAL_DIRECTORY_PATH,
                                       title=DOWNLOAD_LOCATION_DIALOG_TITLE)

    def run(self) -> None:
        thread = threading.Thread(target=self.__torrentClient.start)
        thread.start()
        self.__refreshModel()
        self.__mainWindow.mainloop()

    def __refreshModel(self) -> None:
        REFRESH_INTERVAL_IN_MILLISECONDS: Final[int] = 1000
        self.__treeViewLogic.refreshModel()
        self.__mainWindow.after(REFRESH_INTERVAL_IN_MILLISECONDS, self.__refreshModel)
