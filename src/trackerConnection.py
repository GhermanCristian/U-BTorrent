from typing import List, Final, Tuple
import requests
from bencode3 import bdecode
from requests import Response
from domain.peer import Peer


class TrackerConnection:
    PORT: Final[int] = 6881
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"
    REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
    PEERS_PART_HEADER: Final[str] = "5:peers"
    PEER_SIZE: Final[int] = 6  # bytes

    """
    Determines the list of peers from the tracker response
    @:param peersPart - a string containing some headers and the extended ASCII-encoded values representing the IP:port of the peers
    The header starts with "5:peers" - part of the bencode standard, then a decimal number = the number of bytes needed for the IPs and ports, which is followed by a colon.
    The decimal number has to be a multiple of 6 (4 bytes for each IP, 2 for each port)
    @:return a list of Peer objects, extracted from the input
    """
    def computePeers(self, peersPart: str) -> List[Peer]:
        peerAddressList: List[Peer] = []
        currentIndex: int = len(self.PEERS_PART_HEADER)  # skip the "5:peers" part
        peersByteCount: int = 0  # the number of bytes used to represent peer addresses

        while peersPart[currentIndex].isdigit():
            peersByteCount = peersByteCount * 10 + int(peersPart[currentIndex])
            currentIndex += 1
        currentIndex += 1  # skip the ":"
        assert peersByteCount % self.PEER_SIZE == 0
        
        for _ in range(0, peersByteCount // self.PEER_SIZE):
            currentIP = ord(peersPart[currentIndex]) * 256**3 + ord(peersPart[currentIndex + 1]) * 256**2 + ord(peersPart[currentIndex + 2]) * 256 + ord(peersPart[currentIndex + 3])
            currentPort = ord(peersPart[currentIndex + 4]) * 256 + ord(peersPart[currentIndex + 5])
            peerAddressList.append(Peer(currentIP, currentPort))
            currentIndex += self.PEER_SIZE

        return peerAddressList

    """
    Processes the tracker response
    @:param responseText - the response to the GET request made to the tracker
    """
    def onSuccessfulConnection(self, responseText: str) -> Tuple[dict, List[Peer]]:
        peersPartStartingPosition: int = responseText.find(self.PEERS_PART_HEADER)
        peersPart: str = responseText[peersPartStartingPosition: -1]
        nonPeersPart: dict = bdecode(str.encode(responseText.replace(peersPart, "")))
        return nonPeersPart, self.computePeers(peersPart)

    """
    Computes the peer list according to the torrent meta info file
    @:param announceURL - the URL of the tracker
    @:param infoHash - hash value of the "info" section in the torrent meta info file
    @:param totalSize - total size of the content
    """
    def getPeerList(self, announceURL, infoHash, totalSize) -> None:
        payload = {
            "info_hash": infoHash,
            "peer_id": self.PEER_ID,
            "port": self.PORT,
            "uploaded": "0",
            "downloaded": "0",
            "left": totalSize,
            "compact": 1
        }

        while True:
            print("Start")
            try:
                response: Response = requests.get(announceURL, params=payload, timeout=self.REQUEST_ATTEMPT_TIMEOUT)
                if response.status_code == 200:
                    nonPeersPart, peerList = self.onSuccessfulConnection(response.text)
                    print(nonPeersPart)
                    for peer in peerList:
                        print(peer)
                    return
            except Exception as e:
                print("Error - ", e)
