from typing import List, Final, Tuple
import requests
from bencode3 import bdecode
from requests import Response
from domain.peer import Peer


class TrackerConnection:
    PORT: Final[int] = 6881
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"
    REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
    PEERS_PART_HEADER: Final[bytes] = b"5:peers"
    PEER_SIZE: Final[int] = 6  # bytes

    """
    Determines the list of peers from the tracker response
    @:param peersPart - a bytearray containing some headers and the extended ASCII-encoded values representing the IP:port of the peers
    The header starts with "5:peers" - part of the bencode standard, then a decimal number = the number of bytes needed for the IPs and ports, which is followed by a colon.
    The decimal number has to be a multiple of 6 (4 bytes for each IP, 2 for each port)
    @:return a list of Peer objects, extracted from the input
    """
    def computePeers(self, peersPart: bytearray) -> List[Peer]:
        peerAddressList: List[Peer] = []
        currentIndex: int = len(self.PEERS_PART_HEADER)  # skip the "5:peers" part
        peersByteCount: int = 0  # the number of bytes used to represent peer addresses

        while 48 + 0 <= peersPart[currentIndex] <= 48 + 9:
            peersByteCount = peersByteCount * 10 + peersPart[currentIndex] - 48
            currentIndex += 1
        currentIndex += 1  # skip the ":"
        assert peersByteCount % self.PEER_SIZE == 0, "The number of bytes for the peers IPs and ports should be a multiple of {0}".format(self.PEER_SIZE)
        
        for _ in range(0, peersByteCount // self.PEER_SIZE):
            currentIP = peersPart[currentIndex] * 256**3 + peersPart[currentIndex + 1] * 256**2 + peersPart[currentIndex + 2] * 256 + peersPart[currentIndex + 3]
            currentPort = peersPart[currentIndex + 4] * 256 + peersPart[currentIndex + 5]
            peerAddressList.append(Peer(currentIP, currentPort))
            currentIndex += self.PEER_SIZE

        return peerAddressList

    """
    Processes the tracker response
    @:param responseBytes - the response to the GET request made to the tracker
    """
    def onSuccessfulConnection(self, responseBytes: bytes) -> Tuple[dict, List[Peer]]:
        responseAsByteArray: bytearray = bytearray(responseBytes)
        peersPartStartingPosition: int = responseAsByteArray.find(self.PEERS_PART_HEADER)
        peersPart: bytearray = responseAsByteArray[peersPartStartingPosition: -1]
        nonPeersPart: dict = bdecode(responseAsByteArray.replace(peersPart, b""))
        return nonPeersPart, self.computePeers(peersPart)

    """
    Computes the peer list according to the torrent meta info file
    @:param announceURL - the URL of the tracker
    @:param infoHash - hash value of the "info" section in the torrent meta info file
    @:param totalSize - total size of the content
    """
    def getPeerList(self, announceURL: str, infoHash: bytes, totalSize: int) -> None:
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
                    nonPeersPart, peerList = self.onSuccessfulConnection(response.content)
                    print(nonPeersPart)
                    for peer in peerList:
                        print(peer)
                    return
            except Exception as e:
                print("Error - ", e)
