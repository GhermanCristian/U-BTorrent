import hashlib
import math
from typing import List, Final
from bencode3 import bdecode, bencode
from domain.file import File


class TorrentMetaInfoScanner:
    READ_BINARY_MODE: Final[str] = "rb"
    LOCATION_SEPARATOR: Final[str] = "/"
    FILE_PATH_KEY: Final[str] = "path"
    FILE_LENGTH_KEY: Final[str] = "length"
    SINGLE_FILE_MODE_LENGTH_KEY: Final[str] = "length"
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

    """
    @:param file - dictionary which contains information about a file
    """
    def __loadInfoAboutFile(self, file: dict) -> None:
        path: str = ""
        for locationPart in file[self.FILE_PATH_KEY]:
            path += locationPart + self.LOCATION_SEPARATOR
        path = path[:-1]  # remove trailing "/"
        self.__files.append(File(path, int(file[self.FILE_LENGTH_KEY])))

    """
    Determines if the current torrent contains multiple files or just one
    @:param info - dictionary with information about the torrent content
    @:return true, if the torrent contains multiple files; false, otherwise
    """
    def __multipleFileMode(self, info: dict) -> bool:
        return self.FILES_KEY in info.keys()

    """
    Decodes a torrent meta info file, and loads in memory all the necessary fields
    """
    def __decodeTorrentFile(self) -> None:
        with open(self.__torrentFileLocation, self.READ_BINARY_MODE) as torrentFile:
            content: dict = bdecode(torrentFile.read())
            self.__announceURL = content[self.ANNOUNCE_KEY]
            self.__announceURLList = content[self.ANNOUNCE_LIST_KEY]

            info: dict = content[self.INFO_KEY]
            self.__infoHash = hashlib.sha1(bencode(info)).digest()
            # in single-file mode, this becomes the name of the file itself
            self.__torrentName = info[self.TORRENT_NAME_KEY]
            self.__pieceLength = int(info[self.PIECE_LENGTH_KEY])
            self.__pieces = info[self.PIECES_KEY]
            if self.__multipleFileMode(info):
                for file in info[self.FILES_KEY]:
                    self.__loadInfoAboutFile(file)
            else:
                self.__files.append(File(self.__torrentName, info[self.SINGLE_FILE_MODE_LENGTH_KEY]))

    def getAnnounceURL(self) -> str:
        return self.__announceURL

    def getAnnounceURLList(self) -> List[str]:
        return self.__announceURLList

    def getTorrentName(self) -> str:
        return self.__torrentName

    def getPieceLength(self) -> int:
        return self.__pieceLength

    def getPieceCount(self) -> int:
        return math.ceil(self.getTotalContentSize() / self.__pieceLength)

    def getFinalPieceLength(self) -> int:
        return self.getTotalContentSize() % self.__pieceLength

    def getPieces(self) -> bytes:
        return self.__pieces

    def getPieceHash(self, pieceIndex: int) -> bytes:
        return self.__pieces[pieceIndex * 20: (pieceIndex + 1) * 20]

    def getFiles(self) -> List[File]:
        return self.__files

    def getInfoHash(self) -> bytes:
        return self.__infoHash

    def getTotalContentSize(self) -> int:
        return sum(file.length for file in self.__files)
