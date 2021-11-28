from TorrentMetaInfoScanner import TorrentMetaInfoScanner


def main():
    scanner = TorrentMetaInfoScanner("Resources/NBALOGO_archive.torrent")
    print(scanner.getAnnounceURL())
    print(scanner.getAnnounceURLList())
    print(scanner.getTorrentName())
    print(scanner.getPieceLength())
    print(scanner.getPieces())
    for file in scanner.getFiles():
        print(file)


if __name__ == "__main__":
    main()
