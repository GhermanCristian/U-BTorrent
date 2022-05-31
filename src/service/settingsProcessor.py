from configparser import ConfigParser
from typing import Final

"""This class is basically a singleton"""
SETTINGS_FILE_PATH: Final[str] = "..\\Resources\\settings.ini"
configParser: ConfigParser = ConfigParser()
configParser.read(SETTINGS_FILE_PATH)


def getDownloadLocation() -> str:
    return configParser["DEFAULT"]["initialDownloadLocation"]


def getUserInterfaceRefreshRate() -> int:
    return configParser.getint("DEFAULT", "userInterfaceRefreshRate")
