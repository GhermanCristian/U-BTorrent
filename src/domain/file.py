class File:
    def __init__(self, path: str, sha1: str, length: int):
        self.__path: str = path
        self.__sha1: str = sha1
        self.__length: int = length

    @property
    def path(self) -> str:
        return self.__path

    @property
    def sha1(self) -> str:
        return self.__sha1

    @property
    def length(self) -> int:
        return self.__length

    def __str__(self) -> str:
        return self.__path + "; sha1=" + self.__sha1 + "; size=" + str(self.__length) + "B"

    def __eq__(self, other):
        return isinstance(other, File) and self.__path == other.path and self.__sha1 == other.sha1 and self.__length == other.length
