from tkinter import Tk, Toplevel
from typing import Final


class AboutUBTorrentWindow:
    def __init__(self, mainWindow: Tk):
        self.__aboutUBTorrentWindow: Toplevel = self.__createAboutUBTorrentWindow(mainWindow)
        
    def __createAboutUBTorrentWindow(self, mainWindow: Tk) -> Toplevel:
        ABOUT_UBTORRENT_WINDOW_TITLE: Final[str] = "About U-BTorrent"
        ABOUT_UBTORRENT_WINDOW_MIN_WIDTH_IN_PIXELS: Final[int] = 640
        ABOUT_UBTORRENT_WINDOW_MIN_HEIGHT_IN_PIXELS: Final[int] = 480

        aboutUBTorrentWindow: Toplevel = Toplevel()
        aboutUBTorrentWindow.title(ABOUT_UBTORRENT_WINDOW_TITLE)
        aboutUBTorrentWindow.minsize(ABOUT_UBTORRENT_WINDOW_MIN_WIDTH_IN_PIXELS, ABOUT_UBTORRENT_WINDOW_MIN_HEIGHT_IN_PIXELS)
        aboutUBTorrentWindow.transient(mainWindow)  # so that the window is not covered by the main window after exiting the directory dialog
        return aboutUBTorrentWindow
