from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


def main():
    scanner = TorrentMetaInfoScanner("Resources/NBALOGO_archive.torrent")
    print(scanner.getAnnounceURL())
    print(scanner.getAnnounceURLList())
    print(scanner.getTorrentName())
    print(scanner.getPieceLength())
    print(scanner.getPieces())
    for file in scanner.getFiles():
        print(file)
    print(scanner.getInfoHash())
    print(scanner.getTotalContentSize())

    TrackerConnection().getPeerList(scanner.getAnnounceURL(), scanner.getInfoHash(), scanner.getTotalContentSize())


if __name__ == "__main__":
    main()
