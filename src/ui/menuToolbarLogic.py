from tkinter import Menu, Tk
from typing import Final


class MenuToolbarLogic:
    def __init__(self, mainWindow: Tk):
        self.__mainWindow: Tk = mainWindow

    def __settingsCommand(self) -> None:
        pass

    def __helpCommand(self) -> None:
        pass

    def __aboutCommand(self) -> None:
        pass

    def createMenuToolbar(self) -> Menu:
        SETTINGS_COMMAND_LABEL: Final[str] = "Settings"
        HELP_COMMAND_LABEL: Final[str] = "Help"
        ABOUT_COMMAND_LABEL: Final[str] = "About"

        menuBar: Menu = Menu(self.__mainWindow)
        menuBar.add_command(label=SETTINGS_COMMAND_LABEL, command=self.__settingsCommand)
        menuBar.add_command(label=HELP_COMMAND_LABEL, command=self.__helpCommand)
        menuBar.add_command(label=ABOUT_COMMAND_LABEL, command=self.__aboutCommand)
        return menuBar
