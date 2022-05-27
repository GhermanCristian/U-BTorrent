from concurrent.futures import ThreadPoolExecutor
from service.processSingleTorrent import ProcessSingleTorrent


def startTorrent(torrentFileLocation: str) -> None:
    ProcessSingleTorrent(torrentFileLocation)


def main():
    with ThreadPoolExecutor(3) as executor:
        executor.submit(startTorrent, "..\\Resources\\medical.torrent")
        executor.submit(startTorrent, "..\\Resources\\mars.torrent")
        executor.submit(startTorrent, "..\\Resources\\ppcoin.torrent")


if __name__ == "__main__":
    main()
