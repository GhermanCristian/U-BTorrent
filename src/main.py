from typing import List
from domain.peer import Peer
from peerCommunication import PeerCommunication
from torrentMetaInfoScanner import TorrentMetaInfoScanner
from trackerConnection import TrackerConnection


def main():
    scanner: TorrentMetaInfoScanner = TorrentMetaInfoScanner("Resources/Tails 4.28 64Bit ISO.torrent")
    peerList: List[Peer] = TrackerConnection().getPeerList(scanner.getAnnounceURL(), scanner.getInfoHash(), scanner.getTotalContentSize())
    PeerCommunication(peerList, scanner.getInfoHash(), TrackerConnection.PEER_ID).start()


if __name__ == "__main__":
    main()
