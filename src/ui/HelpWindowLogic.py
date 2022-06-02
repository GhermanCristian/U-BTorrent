from tkinter import Toplevel, Tk
from typing import Final


class HelpWindowLogic:
    def __init__(self, mainWindow: Tk):
        self.__helpWindow: Toplevel = self.__createHelpWindow(mainWindow)

    def __createHelpWindow(self, mainWindow: Tk) -> Toplevel:
        HELP_WINDOW_TITLE: Final[str] = "Help"
        HELP_WINDOW_MIN_WIDTH_IN_PIXELS: Final[int] = 640
        HELP_WINDOW_MIN_HEIGHT_IN_PIXELS: Final[int] = 480

        helpWindow: Toplevel = Toplevel()
        helpWindow.title(HELP_WINDOW_TITLE)
        helpWindow.minsize(HELP_WINDOW_MIN_WIDTH_IN_PIXELS, HELP_WINDOW_MIN_HEIGHT_IN_PIXELS)
        helpWindow.transient(mainWindow)  # so that the window is not covered by the main window after exiting the directory dialog
        return helpWindow
