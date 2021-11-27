from bcoding import bdecode  # TODO - add this library to the theoretical part
from typing import List, Dict, Final


class TorrentMetaInfoScanner:
    def __decodeTorrentFile(self) -> None:
        with open(self.__torrentFileLocation, "rb") as torrentFile:
            content: dict = bdecode(torrentFile)
            self.__announceURL = content["announce"]
            self.__announceURLList = content["announce-list"]

            info: dict = content["info"]
            self.__torrentName = info["name"]
            self.__pieceLength = int(info["piece length"])
            self.__pieces = info["pieces"]
            for file in info["files"]:
                path: str = ""
                for locationPart in file["path"]:
                    path += locationPart + "/"
                path = path[:-1]  # remove trailing "/"
                self.__files[path] = file  # TODO - create a File class

    def __init__(self, torrentFileLocation: str):
        self.__torrentFileLocation: Final[str] = torrentFileLocation

        self.__announceURL: str = ""
        self.__announceURLList: List[str] = []
        self.__torrentName: str = ""
        self.__pieceLength: int = 0
        self.__pieces: str = ""
        self.__files: Dict = {}

        self.__decodeTorrentFile()

    def getAnnounceURL(self) -> str:
        return self.__announceURL

    def getAnnounceURLList(self) -> List[str]:
        return self.__announceURLList

    def getTorrentName(self) -> str:
        return self.__torrentName

    def getPieceLength(self) -> int:
        return self.__pieceLength

    def getPieces(self) -> str:
        return self.__pieces

    def getFiles(self) -> Dict:
        return self.__files
