from typing import List
from domain.peer import Peer
from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


def printScannerInformation(scanner: TorrentMetaInfoScanner) -> None:
    print(scanner.getAnnounceURL())
    print(scanner.getAnnounceURLList())
    print(scanner.getTorrentName())
    print(scanner.getPieceLength())
    print(scanner.getPieces())
    for file in scanner.getFiles():
        print(file)
    print(scanner.getInfoHash())
    print(scanner.getTotalContentSize())


def printPeerList(scanner: TorrentMetaInfoScanner) -> None:
    peerList: List[Peer] = TrackerConnection().getPeerList(scanner.getAnnounceURL(), scanner.getInfoHash(), scanner.getTotalContentSize())
    for peer in peerList:
        print(peer)


def main():
    scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner("Resources/NBALOGO_archive.torrent")
    printScannerInformation(scanner)
    printPeerList(scanner)


if __name__ == "__main__":
    main()
