import threading
from tkinter import *
from tkinter import filedialog
from typing import Final, Tuple
from service import settingsProcessor
from service.torrentClient import TorrentClient
from ui import utilsGUI
from ui.menuToolbar import MenuToolbar
from ui.torrentList import TorrentList


class GUI:
    REFRESH_INTERVAL_IN_MILLISECONDS: Final[int] = settingsProcessor.getUserInterfaceRefreshRate()

    def __init__(self):
        self.__mainWindow: Tk = self.__createMainWindow()
        menuBar: Menu = MenuToolbar(self.__mainWindow).createMenuToolbar()
        self.__mainWindow.config(menu=menuBar)
        
        torrentFilesPaths: Tuple[str, ...] = self.__selectTorrentFilesPaths()
        self.__torrentClient: TorrentClient = TorrentClient(torrentFilesPaths, settingsProcessor.getDownloadLocation())

        self.__treeViewLogic: TorrentList = TorrentList(self.__mainWindow, self.__torrentClient.singleTorrentProcessors)

    def __createMainWindow(self) -> Tk:
        WINDOW_TITLE: Final[str] = "U-BTorrent"
        MIN_WINDOW_WIDTH_IN_PIXELS: Final[int] = 1100
        MIN_WINDOW_HEIGHT_IN_PIXELS: Final[int] = 480
        APPLY_TO_ALL_WINDOWS: Final[bool] = True

        mainWindow: Tk = Tk()
        mainWindow.title(WINDOW_TITLE)
        mainWindow.minsize(MIN_WINDOW_WIDTH_IN_PIXELS, MIN_WINDOW_HEIGHT_IN_PIXELS)
        mainWindow.iconphoto(APPLY_TO_ALL_WINDOWS, PhotoImage(file=utilsGUI.LOGO_PATH))
        return mainWindow

    def __selectTorrentFilesPaths(self) -> Tuple[str, ...]:
        FILE_DIALOG_TITLE: Final[str] = "Select .torrent files"
        FILE_TYPE_DESCRIPTION: Final[str] = ".torrent files"
        DOT_TORRENT_FILE_PATTERN: Final[str] = "*.torrent"

        return filedialog.askopenfilenames(initialdir=utilsGUI.INITIAL_DIRECTORY_PATH,
                                           title=FILE_DIALOG_TITLE,
                                           filetypes=((FILE_TYPE_DESCRIPTION, DOT_TORRENT_FILE_PATTERN),))

    def run(self) -> None:
        thread = threading.Thread(target=self.__torrentClient.start)
        thread.start()
        self.__refreshModel()
        try:
            self.__mainWindow.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.__torrentClient.stop()

    def __refreshModel(self) -> None:
        self.__treeViewLogic.refreshModel()
        self.__mainWindow.after(self.REFRESH_INTERVAL_IN_MILLISECONDS, self.__refreshModel)
