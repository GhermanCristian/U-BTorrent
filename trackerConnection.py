import requests
from bencode3 import bdecode


class TrackerConnection:
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



