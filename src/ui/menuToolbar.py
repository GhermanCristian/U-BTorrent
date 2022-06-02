from tkinter import Menu, Tk
from typing import Final
from ui import utilsGUI
from ui.helpWindow import HelpWindow
from ui.settingsWindow import SettingsWindow


class MenuToolbar:
    def __init__(self, mainWindow: Tk):
        self.__mainWindow: Tk = mainWindow

    def __settingsCommand(self) -> None:
        SettingsWindow(self.__mainWindow)

    def __helpCommand(self) -> None:
        HelpWindow(self.__mainWindow)

    def __aboutUBTorrentCommand(self) -> None:
        pass

    def __sendFeedbackCommand(self) -> None:
        pass

    def createMenuToolbar(self) -> Menu:
        SETTINGS_COMMAND_LABEL: Final[str] = "Settings"
        HELP_COMMAND_LABEL: Final[str] = "Help"
        ABOUT_SUBMENU_LABEL: Final[str] = "About"
        ABOUT_UBTORRENT_COMMAND_LABEL: Final[str] = "About U-BTorrent"
        SEND_FEEDBACK_COMMAND_LABEL: Final[str] = "Send feedback"

        # can't change the menu style bc Windows
        menuBar: Menu = Menu(self.__mainWindow)
        menuBar.add_command(label=SETTINGS_COMMAND_LABEL, command=self.__settingsCommand)
        menuBar.add_command(label=HELP_COMMAND_LABEL, command=self.__helpCommand)
        aboutSubMenu: Menu = Menu(menuBar, tearoff=utilsGUI.NO_MENU_TEAROFF)
        aboutSubMenu.add_command(label=ABOUT_UBTORRENT_COMMAND_LABEL, command=self.__aboutUBTorrentCommand)
        aboutSubMenu.add_separator()
        aboutSubMenu.add_command(label=SEND_FEEDBACK_COMMAND_LABEL, command=self.__sendFeedbackCommand)
        menuBar.add_cascade(label=ABOUT_SUBMENU_LABEL, menu=aboutSubMenu)
        return menuBar
