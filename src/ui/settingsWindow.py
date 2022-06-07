from tkinter import Toplevel, Label, Button, filedialog, Tk
from tkinter.ttk import Separator, Entry
from typing import Final, Literal
from service import settingsProcessor
from ui import utilsGUI


class SettingsWindow:
    X_PADDING: Final[int] = 15
    Y_PADDING: Final[int] = 15
    NORMAL_FONT_SIZE: Final[int] = 12

    DOWNLOAD_LOCATION_ROW_INDEX: Final[int] = 1
    REFRESH_RATE_ROW_INDEX: Final[int] = 3

    def __init__(self, mainWindow: Tk):
        self.__settingsWindow: Toplevel = self.__createSettingsWindow(mainWindow)

        self.__createDownloadLocationInfo()
        self.__downloadLocationField: Label = self.__createDownloadLocationField()
        self.__createChooseNewLocationButton()
        self.__displaySeparator(self.DOWNLOAD_LOCATION_ROW_INDEX + 1)

        self.__createRefreshRateInfo()
        self.__refreshRateEntry: Entry = self.__createRefreshRateEntry()
        self.__createSaveRefreshRateButton()
        self.__displaySeparator(self.REFRESH_RATE_ROW_INDEX + 1)

        self.__createRestartWarningLabel(self.REFRESH_RATE_ROW_INDEX + 2)

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
        DOWNLOAD_LOCATION_INFO_COLUMN_SPAN: Final[int] = 3

        downloadLocationInfoLabel: Label = Label(self.__settingsWindow,
                                                 text=DOWNLOAD_LOCATION_INFO_TEXT,
                                                 font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE))
        downloadLocationInfoLabel.grid(row=self.DOWNLOAD_LOCATION_ROW_INDEX,
                                       columnspan=DOWNLOAD_LOCATION_INFO_COLUMN_SPAN,
                                       padx=self.X_PADDING,
                                       pady=self.Y_PADDING)

    def __createDownloadLocationField(self) -> Label:
        DOWNLOAD_LOCATION_FIELD_COLUMN: Final[int] = 4
        DOWNLOAD_LOCATION_FIELD_COLUMN_SPAN: Final[int] = 10

        downloadLocationField: Label = Label(self.__settingsWindow,
                                             text=settingsProcessor.getDownloadLocation(),
                                             font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE),
                                             bg=utilsGUI.CREAM_COLOR)
        downloadLocationField.grid(row=self.DOWNLOAD_LOCATION_ROW_INDEX,
                                   column=DOWNLOAD_LOCATION_FIELD_COLUMN,
                                   columnspan=DOWNLOAD_LOCATION_FIELD_COLUMN_SPAN,
                                   padx=self.X_PADDING,
                                   pady=self.Y_PADDING)
        return downloadLocationField

    def __createChooseNewLocationButton(self) -> None:
        CHOOSE_NEW_LOCATION_BUTTON_TEXT: Final[str] = "Select"
        CHOOSE_NEW_LOCATION_BUTTON_COLUMN: Final[int] = 14

        chooseNewLocationButton: Button = Button(self.__settingsWindow,
                                                 text=CHOOSE_NEW_LOCATION_BUTTON_TEXT,
                                                 command=self.__setNewDownloadLocation,
                                                 font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE))
        chooseNewLocationButton.grid(row=self.DOWNLOAD_LOCATION_ROW_INDEX,
                                     column=CHOOSE_NEW_LOCATION_BUTTON_COLUMN,
                                     padx=self.X_PADDING,
                                     pady=self.Y_PADDING)

    def __selectBaseDownloadLocation(self) -> str:
        DOWNLOAD_LOCATION_DIALOG_TITLE: Final[str] = "Select the download location"
        return filedialog.askdirectory(initialdir=settingsProcessor.getDownloadLocation(),
                                       title=DOWNLOAD_LOCATION_DIALOG_TITLE)

    def __setNewDownloadLocation(self) -> None:
        newDownloadLocation: str = self.__selectBaseDownloadLocation()
        self.__downloadLocationField.config(text=newDownloadLocation)
        settingsProcessor.setDownloadLocation(newDownloadLocation)

    def __displaySeparator(self, rowIndex: int) -> None:
        SEPARATOR_ORIENTATION: Final[Literal["horizontal", "vertical"]] = "horizontal"
        FIRST_COLUMN: Final[int] = 1
        COLUMN_SPAN: Final[int] = 13
        HORIZONTAL_STICKY: Final[str] = "ew"

        separator = Separator(self.__settingsWindow,
                              orient=SEPARATOR_ORIENTATION)
        separator.grid(row=rowIndex,
                       column=FIRST_COLUMN,
                       columnspan=COLUMN_SPAN,
                       sticky=HORIZONTAL_STICKY,
                       pady=self.Y_PADDING)

    def __createRefreshRateInfo(self) -> None:
        REFRESH_RATE_INFO_TEXT: Final[str] = "Refresh rate (in milliseconds)"
        REFRESH_RATE_INFO_COLUMN_SPAN: Final[int] = 3

        refreshRateInfoLabel: Label = Label(self.__settingsWindow,
                                            text=REFRESH_RATE_INFO_TEXT,
                                            font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE))
        refreshRateInfoLabel.grid(row=self.REFRESH_RATE_ROW_INDEX,
                                  columnspan=REFRESH_RATE_INFO_COLUMN_SPAN,
                                  padx=self.X_PADDING,
                                  pady=self.Y_PADDING)

    def __createRefreshRateEntry(self) -> Entry:
        REFRESH_RATE_ENTRY_COLUMN: Final[int] = 4
        REFRESH_RATE_ENTRY_COLUMN_SPAN: Final[int] = 3
        POSITION_TO_INSERT_TEXT_AT: Final[int] = 0

        entry: Entry = Entry(self.__settingsWindow,
                             font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE))
        entry.insert(POSITION_TO_INSERT_TEXT_AT, str(settingsProcessor.getUserInterfaceRefreshRate()))
        entry.grid(row=self.REFRESH_RATE_ROW_INDEX,
                   column=REFRESH_RATE_ENTRY_COLUMN,
                   columnspan=REFRESH_RATE_ENTRY_COLUMN_SPAN,
                   padx=self.X_PADDING,
                   pady=self.Y_PADDING)
        return entry

    def __createSaveRefreshRateButton(self) -> None:
        SAVE_REFRESH_RATE_BUTTON_TEXT: Final[str] = "Save"
        SAVE_REFRESH_RATE_BUTTON_COLUMN: Final[int] = 14

        saveRefreshRateButton: Button = Button(self.__settingsWindow,
                                               text=SAVE_REFRESH_RATE_BUTTON_TEXT,
                                               command=self.__saveRefreshRate,
                                               font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE))
        saveRefreshRateButton.grid(row=self.REFRESH_RATE_ROW_INDEX,
                                   column=SAVE_REFRESH_RATE_BUTTON_COLUMN,
                                   padx=self.X_PADDING,
                                   pady=self.Y_PADDING)

    def __saveRefreshRate(self) -> None:
        newRefreshRate: str = self.__refreshRateEntry.get()
        settingsProcessor.setUserInterfaceRefreshRate(newRefreshRate)

    def __createRestartWarningLabel(self, rowIndex: int) -> None:
        RESTART_WARNING_LABEL_TEXT: Final[str] = "Any changes made will be applied after restarting the program"
        RESTART_WARNING_LABEL_COLUMN: Final[int] = 4

        restartWarningLabel: Label = Label(self.__settingsWindow,
                                           text=RESTART_WARNING_LABEL_TEXT,
                                           font=(utilsGUI.FONT_NAME, self.NORMAL_FONT_SIZE))
        restartWarningLabel.grid(row=rowIndex,
                                 column=RESTART_WARNING_LABEL_COLUMN,
                                 padx=self.X_PADDING,
                                 pady=self.Y_PADDING)
