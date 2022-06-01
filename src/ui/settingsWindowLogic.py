from tkinter import Toplevel, Label, Button, filedialog, Tk
from typing import Final
from service import settingsProcessor


class SettingsWindowLogic:
    X_PADDING: Final[int] = 15
    Y_PADDING: Final[int] = 15

    def __init__(self, mainWindow: Tk):
        self.__settingsWindow: Toplevel = self.__createSettingsWindow(mainWindow)

        self.__createDownloadLocationInfo()
        self.__downloadLocationField: Label = self.__createDownloadLocationField()
        self.__createChooseNewLocationButton()
        # TODO - add an info label + a field for changing the refresh rate

    def __createSettingsWindow(self, mainWindow: Tk) -> Toplevel:
        SETTINGS_WINDOW_TITLE: Final[str] = "Settings"
        SETTINGS_WINDOW_MIN_WIDTH_IN_PIXELS: Final[int] = 640
        SETTINGS_WINDOW_MIN_HEIGHT_IN_PIXELS: Final[int] = 480

        settingsWindow: Toplevel = Toplevel()
        settingsWindow.title(SETTINGS_WINDOW_TITLE)
        settingsWindow.minsize(SETTINGS_WINDOW_MIN_WIDTH_IN_PIXELS, SETTINGS_WINDOW_MIN_HEIGHT_IN_PIXELS)
        settingsWindow.transient(mainWindow)  # so that the window is not covered by the main window after exiting the directory dialog
        return settingsWindow

    def __createDownloadLocationInfo(self) -> None:
        DOWNLOAD_LOCATION_INFO_TEXT: Final[str] = "Download location"
        DOWNLOAD_LOCATION_INFO_ROW: Final[int] = 1
        DOWNLOAD_LOCATION_INFO_COLUMN_SPAN: Final[int] = 3
        downloadLocationInfoLabel: Label = Label(self.__settingsWindow, text=DOWNLOAD_LOCATION_INFO_TEXT)
        downloadLocationInfoLabel.grid(row=DOWNLOAD_LOCATION_INFO_ROW, columnspan=DOWNLOAD_LOCATION_INFO_COLUMN_SPAN, padx=self.X_PADDING, pady=self.Y_PADDING)

    def __createDownloadLocationField(self) -> Label:
        DOWNLOAD_LOCATION_FIELD_ROW: Final[int] = 1
        DOWNLOAD_LOCATION_FIELD_COLUMN: Final[int] = 4
        DOWNLOAD_LOCATION_FIELD_COLUMN_SPAN: Final[int] = 10
        downloadLocationField: Label = Label(self.__settingsWindow, text=settingsProcessor.getDownloadLocation())
        downloadLocationField.grid(row=DOWNLOAD_LOCATION_FIELD_ROW, column=DOWNLOAD_LOCATION_FIELD_COLUMN, columnspan=DOWNLOAD_LOCATION_FIELD_COLUMN_SPAN, padx=self.X_PADDING, pady=self.Y_PADDING)
        return downloadLocationField

    def __createChooseNewLocationButton(self) -> None:
        CHOOSE_NEW_LOCATION_BUTTON_TEXT: Final[str] = "Select"
        CHOOSE_NEW_LOCATION_BUTTON_ROW: Final[int] = 1
        CHOOSE_NEW_LOCATION_BUTTON_COLUMN: Final[int] = 14
        chooseNewLocationButton: Button = Button(self.__settingsWindow, text=CHOOSE_NEW_LOCATION_BUTTON_TEXT, command=self.__setNewDownloadLocation)
        chooseNewLocationButton.grid(row=CHOOSE_NEW_LOCATION_BUTTON_ROW, column=CHOOSE_NEW_LOCATION_BUTTON_COLUMN, padx=15, pady=15)
        # TODO - warning pop-up or just a label that the changes will come into effect after a restart

    def __selectBaseDownloadLocation(self) -> str:
        DOWNLOAD_LOCATION_DIALOG_TITLE: Final[str] = "Select the download location"
        return filedialog.askdirectory(initialdir=settingsProcessor.getDownloadLocation(),
                                       title=DOWNLOAD_LOCATION_DIALOG_TITLE)

    def __setNewDownloadLocation(self) -> None:
        newDownloadLocation: str = self.__selectBaseDownloadLocation()
        self.__downloadLocationField.config(text=newDownloadLocation)
        settingsProcessor.setDownloadLocation(newDownloadLocation)
