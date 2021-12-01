from typing import List, Final
import requests
from bencode3 import bdecode
from requests import Response
from domain.peer import Peer


class TrackerConnection:
    # TODO - add documentation
    PORT: Final[int] = 6881
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"
    REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds

    def __computePeers(self, peersPart: str) -> List[Peer]:
        peerAddressList: List[Peer] = []
        currentIndex: int = 7  # skip the "5:peers" part
        peersSize: int = 0  # the number of characters which represent peer addresses; it has to be a multiple of 6 (4 for the IP, 2 for the port)

        while peersPart[currentIndex].isdigit():
            peersSize = peersSize * 10 + int(peersPart[currentIndex])
            currentIndex += 1

        currentIndex += 1  # skip the ":"
        assert peersSize % 6 == 0
        for _ in range(0, peersSize // 6):
            currentIP = ord(peersPart[currentIndex]) * 256**3 + ord(peersPart[currentIndex + 1]) * 256**2 + ord(peersPart[currentIndex + 2]) * 256 + ord(peersPart[currentIndex + 3])
            currentPort = ord(peersPart[currentIndex + 4]) * 256 + ord(peersPart[currentIndex + 5])
            peerAddressList.append(Peer(currentIP, currentPort))
            currentIndex += 6

        return peerAddressList

    def __processResponse(self, response: str) -> [str, dict]:
        peersPosition: int = response.find("5:peers")
        peersPart: str = response[peersPosition: -1]
        nonPeersPart: dict = bdecode(str.encode(response.replace(peersPart, "")))
        return [peersPart, nonPeersPart]

    def __onSuccessfulConnection(self, response: Response) -> None:
        peersPart: str
        nonPeersPart: dict
        [peersPart, nonPeersPart] = self.__processResponse(response.text)
        print(peersPart)
        print(nonPeersPart)
        for peer in self.__computePeers(peersPart):
            print(peer)

    def getPeerList(self, announceURL, infoHash, totalSize) -> None:
        payload = {
            "info_hash": infoHash,
            "peer_id": self.PEER_ID,
            "port": self.PORT,
            "uploaded": "0",
            "downloaded": "0",
            "left": totalSize
        }

        while True:
            print("Start")
            try:
                response: Response = requests.get(announceURL, params=payload, timeout=self.REQUEST_ATTEMPT_TIMEOUT)
                if response.status_code == 200:
                    self.__onSuccessfulConnection(response)
                    return
            except Exception as e:
                print("Error - ", e)
