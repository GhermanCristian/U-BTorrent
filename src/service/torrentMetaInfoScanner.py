import hashlib
import math
import os
from typing import List, Final
from bencode3 import bdecode, bencode
from domain.file import File


class TorrentMetaInfoScanner:
    FILES_KEY: Final[str] = "files"  # this is for the case with multiple files - single files use "length"

    def __init__(self, torrentFilePath: str, downloadLocation: str):
        self.__torrentFilePath: Final[str] = torrentFilePath
        self.__rootFolder: str = downloadLocation
        self.__files: List[File] = []
        self.__decodeTorrentFile()

    """
    @:param file - dictionary which contains information about a file
    """
    def __loadInfoAboutFile(self, file: dict) -> None:
        FILE_PATH_KEY: Final[str] = "path"
        FILE_LENGTH_KEY: Final[str] = "length"

        path: str = self.__rootFolder
        for locationPart in file[FILE_PATH_KEY]:
            path = os.path.join(path, locationPart)
        self.__files.append(File(path, int(file[FILE_LENGTH_KEY])))

    """
    Determines if the current torrent contains multiple files or just one
    @:param info - dictionary with information about the torrent content
    @:return True, if the torrent contains multiple files; False, otherwise
    """
    def __multipleFileMode(self, info: dict) -> bool:
        return self.FILES_KEY in info.keys()

    """
    Creates a folder in which the downloaded content will be stored;
    This should only be called for multiple-file torrents; if the location already exists, nothing happens
    """
    def __createRootDownloadFolder(self) -> None:
        try:
            os.mkdir(self.__rootFolder)
        except FileExistsError:
            pass

    def removeRootDownloadFolder(self) -> None:
        os.rmdir(self.__rootFolder)

    """
    Decodes a torrent meta info file, and loads in memory all the necessary fields
    """
    def __decodeTorrentFile(self) -> None:
        READ_BINARY_MODE: Final[str] = "rb"
        SINGLE_FILE_MODE_LENGTH_KEY: Final[str] = "length"
        ANNOUNCE_KEY: Final[str] = "announce"
        ANNOUNCE_LIST_KEY: Final[str] = "announce-list"
        INFO_KEY: Final[str] = "info"
        TORRENT_NAME_KEY: Final[str] = "name"
        PIECE_LENGTH_KEY: Final[str] = "piece length"
        PIECES_KEY: Final[str] = "pieces"

        with open(self.__torrentFilePath, READ_BINARY_MODE) as torrentFile:
            content: dict = bdecode(torrentFile.read())
            self.__announceURL: str = content[ANNOUNCE_KEY]
            self.__announceURLList: List[str] = content[ANNOUNCE_LIST_KEY]
            # TODO - consider the case where the announceURL list is not in the .torrent file

            info: dict = content[INFO_KEY]
            self.__infoHash: bytes = hashlib.sha1(bencode(info)).digest()
            self.__torrentName: str = info[TORRENT_NAME_KEY]  # in single-file mode, this becomes the name of the file itself
            self.__rootFolder = os.path.join(self.__rootFolder, self.__torrentName)
            self.__regularPieceLength: int = int(info[PIECE_LENGTH_KEY])
            self.__pieces: bytes = info[PIECES_KEY]
            if self.__multipleFileMode(info):
                self.__createRootDownloadFolder()
                for file in info[self.FILES_KEY]:
                    self.__loadInfoAboutFile(file)
            else:
                self.__files.append(File(self.__rootFolder, info[SINGLE_FILE_MODE_LENGTH_KEY]))

    @property
    def announceURL(self) -> str:
        return self.__announceURL

    @property
    def announceURLList(self) -> List[str]:
        return self.__announceURLList

    @property
    def torrentName(self) -> str:
        return self.__torrentName

    @property
    def regularPieceLength(self) -> int:
        return self.__regularPieceLength

    @property
    def pieceCount(self) -> int:
        return math.ceil(self.getTotalContentSize() / self.__regularPieceLength)

    @property
    def finalPieceLength(self) -> int:
        return self.getTotalContentSize() % self.__regularPieceLength

    @property
    def pieces(self) -> bytes:
        return self.__pieces

    @property
    def files(self) -> List[File]:
        return self.__files

    @property
    def infoHash(self) -> bytes:
        return self.__infoHash

    def getTotalContentSize(self) -> int:
        return sum(file.length for file in self.__files)

    def getPieceHash(self, pieceIndex: int) -> bytes:
        ENCODED_PIECE_LENGTH: Final[int] = 20
        return self.__pieces[pieceIndex * ENCODED_PIECE_LENGTH: (pieceIndex + 1) * ENCODED_PIECE_LENGTH]
