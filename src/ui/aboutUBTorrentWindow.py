from tkinter import Tk, Toplevel, Label, PhotoImage, TOP, BOTTOM
from typing import Final, Literal
from ui import utilsGUI


class AboutUBTorrentWindow:
    NORMAL_FONT_SIZE: Final[int] = 14
    X_PADDING: Final[int] = 20
    Y_PADDING: Final[int] = 20
    WINDOW_SIZE_IN_PIXELS: Final[int] = 330  # square window
    CENTER_ANCHOR: Final[Literal["center"]] = "center"

    def __init__(self, mainWindow: Tk):
        self.__aboutUBTorrentWindow: Toplevel = self.__createAboutUBTorrentWindow(mainWindow)
        self.__displayLogo()
        self.__displayContent()

    def __createAboutUBTorrentWindow(self, mainWindow: Tk) -> Toplevel:
        ABOUT_UBTORRENT_WINDOW_TITLE: Final[str] = "About U-BTorrent"

        aboutUBTorrentWindow: Toplevel = Toplevel()
        aboutUBTorrentWindow.title(ABOUT_UBTORRENT_WINDOW_TITLE)
        aboutUBTorrentWindow.minsize(self.WINDOW_SIZE_IN_PIXELS, self.WINDOW_SIZE_IN_PIXELS)
        aboutUBTorrentWindow.maxsize(self.WINDOW_SIZE_IN_PIXELS, self.WINDOW_SIZE_IN_PIXELS)
        aboutUBTorrentWindow.transient(mainWindow)  # so that the window is not covered by the main window after exiting the directory dialog
        aboutUBTorrentWindow.resizable(False, False)
        return aboutUBTorrentWindow

    def __displayLogo(self) -> None:
        HALF_SIZE: Final[int] = 2

        logo: PhotoImage = PhotoImage(file=utilsGUI.LOGO_PATH).subsample(HALF_SIZE, HALF_SIZE)
        logoLabel: Label = Label(self.__aboutUBTorrentWindow, image=logo, anchor=self.CENTER_ANCHOR)
        logoLabel.image = logo
        logoLabel.pack(side=TOP)

    def __displayContent(self) -> None:
        content: Final[str] = """Why U-BTorrent ? Because it's simple.
Est. 2022
HAIDE U!"""
        Label(self.__aboutUBTorrentWindow,
              text=content,
              font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE),
              width=self.WINDOW_SIZE_IN_PIXELS,
              anchor=self.CENTER_ANCHOR).pack(side=BOTTOM,
                                    padx=self.X_PADDING,
                                    pady=self.Y_PADDING)

