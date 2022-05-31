from tkinter import Toplevel, Label, Button, filedialog, Tk
from typing import Final
from service import settingsProcessor


class SettingsWindowLogic:
    def __init__(self, mainWindow: Tk):
        self.__settingsWindow: Toplevel = Toplevel()
        self.__settingsWindow.title("Settings")
        self.__settingsWindow.minsize(640, 480)
        self.__settingsWindow.transient(mainWindow)
        label: Label = Label(self.__settingsWindow, text="Default download location")
        label.grid(row=1, columnspan=3, padx=15, pady=15)
        self.__downloadLocationLabel: Label = Label(self.__settingsWindow, text=settingsProcessor.getDownloadLocation())
        self.__downloadLocationLabel.grid(row=1, column=4, columnspan=10, padx=15, pady=15)
        chooseNewLocationButton: Button = Button(self.__settingsWindow, text="Select", command=self.__setNewDownloadLocation)
        chooseNewLocationButton.grid(row=1, column=14, padx=15, pady=15)
        # TODO - warning pop-up or just a label that the changes will come into effect after a restart

    def __selectBaseDownloadLocation(self) -> str:
        DOWNLOAD_LOCATION_DIALOG_TITLE: Final[str] = "Select the download location"
        return filedialog.askdirectory(initialdir=settingsProcessor.getDownloadLocation(),
                                       title=DOWNLOAD_LOCATION_DIALOG_TITLE)

    def __setNewDownloadLocation(self) -> None:
        newDownloadLocation: str = self.__selectBaseDownloadLocation()
        self.__downloadLocationLabel.config(text=newDownloadLocation)
        settingsProcessor.setDownloadLocation(newDownloadLocation)
