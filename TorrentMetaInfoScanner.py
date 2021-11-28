from bcoding import bdecode  # TODO - add the libraries to the theoretical part
from typing import List, Final
from domain.file import File


class TorrentMetaInfoScanner:
    def __loadInfoAboutFile(self, file):
        path: str = ""
        for locationPart in file["path"]:
            path += locationPart + "/"
        path = path[:-1]  # remove trailing "/"
        self.__files.append(File(path, file["sha1"], int(file["length"])))

    def __decodeTorrentFile(self) -> None:
        with open(self.__torrentFileLocation, "rb") as torrentFile:
            content: dict = bdecode(torrentFile)
            self.__announceURL = content["announce"]
            self.__announceURLList = content["announce-list"]

            info: dict = content["info"]
            self.__torrentName = info["name"]
            self.__pieceLength = int(info["piece length"])
            self.__pieces = info["pieces"]
            for file in info["files"]:  # this is for the case with multiple files - single files use "length"
                self.__loadInfoAboutFile(file)

    def __init__(self, torrentFileLocation: str):
        self.__torrentFileLocation: Final[str] = torrentFileLocation

        self.__announceURL: str = ""
        self.__announceURLList: List[str] = []
        self.__torrentName: str = ""
        self.__pieceLength: int = 0
        self.__pieces: str = ""
        self.__files: List[File] = []

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

    def getFiles(self) -> List[File]:
        return self.__files

    def getTotalContentSize(self) -> int:
        # TODO - implement this
        return 0
