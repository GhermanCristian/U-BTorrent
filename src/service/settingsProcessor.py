from configparser import ConfigParser
from typing import Final

"""This class is basically a singleton"""
SETTINGS_FILE_PATH: Final[str] = "..\\Resources\\settings.ini"
configParser: ConfigParser = ConfigParser()
configParser.read(SETTINGS_FILE_PATH)


def updateSettingsFile() -> None:
    with open(SETTINGS_FILE_PATH, "w") as configFile:
        configParser.write(configFile)


def getDownloadLocation() -> str:
    return configParser["DEFAULT"]["initial_download_location"]


def setDownloadLocation(newDownloadLocation: str) -> None:
    configParser.set("DEFAULT", "initial_download_location", newDownloadLocation)
    updateSettingsFile()


def getUserInterfaceRefreshRate() -> int:
    return configParser.getint("DEFAULT", "user_interface_refresh_rate_in_milliseconds")
