import utils


class File:
    def __init__(self, path: str, length: int):
        self.__path: str = path
        self.__length: int = length

    @property
    def path(self) -> str:
        return self.__path

    @property
    def length(self) -> int:
        return self.__length

    def __str__(self) -> str:
        return self.__path + "; size=" + utils.prettyPrintSize(self.__length)

    def __eq__(self, other) -> bool:
        return isinstance(other, File) and self.__path == other.path and self.__length == other.length

    def __hash__(self) -> int:
        return hash((self.__path, self.__length))
