class File:
    def __init__(self, path: str, sha1: str, length: int):
        self.__path: str = path
        self.__sha1: str = sha1
        self.__length: int = length

    @property
    def path(self):
        return self.__path

    @property
    def sha1(self):
        return self.__sha1

    @property
    def length(self):
        return self.__length

    def __str__(self):
        return self.__path + "; sha1=" + self.__sha1 + "; size=" + str(self.__length) + "B"
