from configparser import ConfigParser
from typing import Final

"""This file is basically a singleton"""
SETTINGS_FILE_PATH: Final[str] = "..\\Resources\\settings.ini"
DEFAULT_SECTION_NAME: Final[str] = "DEFAULT"

"""have to use snake case instead of camel case, because the config parser is case-insensitive;
therefore, when it updates the file, it messes-up the key names"""
INITIAL_DOWNLOAD_LOCATION_KEY: Final[str] = "initial_download_location"
USER_INTERFACE_REFRESH_RATE_IN_MILLISECONDS: Final[str] = "user_interface_refresh_rate_in_milliseconds"

configParser: ConfigParser = ConfigParser()
configParser.read(SETTINGS_FILE_PATH)


def updateSettingsFile() -> None:
    WRITE_MODE: Final[str] = "w"
    with open(SETTINGS_FILE_PATH, WRITE_MODE) as configFile:
        configParser.write(configFile)


def getDownloadLocation() -> str:
    return configParser[DEFAULT_SECTION_NAME][INITIAL_DOWNLOAD_LOCATION_KEY]


def setDownloadLocation(newDownloadLocation: str) -> None:
    configParser.set(DEFAULT_SECTION_NAME, INITIAL_DOWNLOAD_LOCATION_KEY, newDownloadLocation)
    updateSettingsFile()


def getUserInterfaceRefreshRate() -> int:
    return configParser.getint(DEFAULT_SECTION_NAME, USER_INTERFACE_REFRESH_RATE_IN_MILLISECONDS)
