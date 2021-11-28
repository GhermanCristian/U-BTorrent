from typing import List, Tuple
import requests
from bencode3 import bdecode


class TrackerConnection:
    def __processPeersPart(self, peersPart: str) -> List[Tuple[int, int]]:
        peerAddressList: List[Tuple[int, int]] = []
        currentIndex: int = 7  # skip the "5:peers" part
        peersSize: int = 0

        while peersPart[currentIndex].isdigit():
            peersSize = peersSize * 10 + int(peersPart[currentIndex])
            currentIndex += 1
        currentIndex += 1  # skip the ":"
        assert peersSize % 6 == 0
        for _ in range(0, peersSize // 6):
            currentIP = ord(peersPart[currentIndex]) * 256**3 + ord(peersPart[currentIndex + 1]) * 256**2 + ord(peersPart[currentIndex + 2]) * 256 + ord(peersPart[currentIndex + 3])
            currentPort = ord(peersPart[currentIndex + 4]) * 256 + ord(peersPart[currentIndex + 5])
            peerAddressList.append((currentIP, currentPort))  # TODO - create a Peer class
            currentIndex += 6

        return peerAddressList

    def __processResponse(self, response: str) -> [str, dict]:
        peersPosition: int = response.find("5:peers")
        peersPart: str = response[peersPosition: -1]
        nonPeersPart: dict = bdecode(str.encode(response.replace(peersPart, "")))
        return [peersPart, nonPeersPart]

    def getPeerList(self, announceURL, infoHash, totalSize):
        payload = {
            "info_hash": infoHash,
            "peer_id": "ABCDEFGHIJKLMNOPQRST",
            "port": "6881",
            "uploaded": "0",
            "downloaded": "0",
            "left": totalSize
        }

        running: bool = True
        peersPart: str
        nonPeersPart: dict
        while running:
            print("Start")
            try:
                r = requests.get(announceURL, params=payload, timeout=30)
                if r.status_code == 200:
                    running = False
                    [peersPart, nonPeersPart] = self.__processResponse(r.text)
            except Exception as e:
                print("Error - ", e)

        print(peersPart)
        print(nonPeersPart)
        print(self.__processPeersPart(peersPart))



