import hashlib
from bencode3 import bdecode, bencode  # TODO - add the libraries to the theoretical part
from typing import List, Final
from domain.file import File


class TorrentMetaInfoScanner:
    # TODO - add documentation
    READ_BINARY: Final[str] = "rb"
    LOCATION_SEPARATOR: Final[str] = "/"
    FILE_PATH_KEY: Final[str] = "path"
    FILE_SHA1_KEY: Final[str] = "sha1"
    FILE_LENGTH_KEY: Final[str] = "length"
    ANNOUNCE_KEY: Final[str] = "announce"
    ANNOUNCE_LIST_KEY: Final[str] = "announce-list"
    INFO_KEY: Final[str] = "info"
    TORRENT_NAME_KEY: Final[str] = "name"
    PIECE_LENGTH_KEY: Final[str] = "piece length"
    PIECES_KEY: Final[str] = "pieces"
    FILES_KEY: Final[str] = "files"  # this is for the case with multiple files - single files use "length"

    def __init__(self, torrentFileLocation: str):
        self.__torrentFileLocation: Final[str] = torrentFileLocation

        self.__announceURL: str
        self.__announceURLList: List[str]
        self.__torrentName: str
        self.__pieceLength: int
        self.__pieces: bytes
        self.__files: List[File] = []
        self.__infoHash: bytes

        self.__decodeTorrentFile()

    def __loadInfoAboutFile(self, file):
        path: str = ""
        for locationPart in file[self.FILE_PATH_KEY]:
            path += locationPart + self.LOCATION_SEPARATOR
        path = path[:-1]  # remove trailing "/"
        self.__files.append(File(path, file[self.FILE_SHA1_KEY], int(file[self.FILE_LENGTH_KEY])))

    def __decodeTorrentFile(self) -> None:
        with open(self.__torrentFileLocation, self.READ_BINARY) as torrentFile:
            content: dict = bdecode(torrentFile.read())
            self.__announceURL = content[self.ANNOUNCE_KEY]
            self.__announceURLList = content[self.ANNOUNCE_LIST_KEY]

            info: dict = content[self.INFO_KEY]
            self.__infoHash = hashlib.sha1(bencode(info)).digest()
            self.__torrentName = info[self.TORRENT_NAME_KEY]
            self.__pieceLength = int(info[self.PIECE_LENGTH_KEY])
            self.__pieces = info[self.PIECES_KEY]
            for file in info[self.FILES_KEY]:
                # TODO - handle the case where there is just 1 file
                self.__loadInfoAboutFile(file)

    def getAnnounceURL(self) -> str:
        return self.__announceURL

    def getAnnounceURLList(self) -> List[str]:
        return self.__announceURLList

    def getTorrentName(self) -> str:
        return self.__torrentName

    def getPieceLength(self) -> int:
        return self.__pieceLength

    def getPieces(self) -> bytes:
        return self.__pieces

    def getFiles(self) -> List[File]:
        return self.__files

    def getInfoHash(self) -> bytes:
        return self.__infoHash

    def getTotalContentSize(self) -> int:
        return sum(file.length for file in self.__files)
