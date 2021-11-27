from TorrentMetaInfoScanner import TorrentMetaInfoScanner


def main():
    scanner = TorrentMetaInfoScanner("Resources/NBALOGO_archive.torrent")
    print(scanner.getAnnounceURL())
    print(scanner.getAnnounceURLList())
    print(scanner.getTorrentName())
    print(scanner.getPieceLength())
    print(scanner.getPieces())
    print(scanner.getFiles())


if __name__ == "__main__":
    main()
