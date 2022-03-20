from typing import List, Final, Tuple
import requests
from bencode3 import bdecode
from requests import Response
from domain.peer import Peer


class TrackerConnection:
    FIRST_AVAILABLE_PORT: Final[int] = 6881
    LAST_AVAILABLE_PORT: Final[int] = 6889
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"
    REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
    PEERS_PART_HEADER: Final[bytes] = b"5:peers"
    PEER_SIZE: Final[int] = 6  # bytes
    ATTEMPTS_TO_CONNECT_TO_TRACKER: Final[int] = 3
    SUCCESS_STATUS_CODE: Final[int] = 200
    PAYLOAD_INFO_HASH_KEY: Final[str] = "info_hash"
    PAYLOAD_PEER_ID_KEY: Final[str] = "peer_id"
    PAYLOAD_PORT_KEY: Final[str] = "port"
    PAYLOAD_UPLOADED_KEY: Final[str] = "uploaded"
    PAYLOAD_DOWNLOADED_KEY: Final[str] = "downloaded"
    PAYLOAD_LEFT_KEY: Final[str] = "left"
    PAYLOAD_COMPACT_KEY: Final[str] = "compact"
    PAYLOAD_EVENT_KEY: Final[str] = "event"
    PAYLOAD_EVENT_STARTED: Final[str] = "started"

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
        assert peersByteCount % self.PEER_SIZE == 0, f"The number of bytes for the peers IPs and ports should be a multiple of {self.PEER_SIZE}"
        
        for _ in range(0, peersByteCount // self.PEER_SIZE):
            currentIP = peersPart[currentIndex] * 256**3 + peersPart[currentIndex + 1] * 256**2 + peersPart[currentIndex + 2] * 256 + peersPart[currentIndex + 3]
            currentPort = peersPart[currentIndex + 4] * 256 + peersPart[currentIndex + 5]
            peerAddressList.append(Peer(currentIP, currentPort))
            currentIndex += self.PEER_SIZE

        return peerAddressList

    # TODO - separate trackerConnection and the part which parses the tracker response
    """
    Processes the tracker response
    @:param responseBytes - the response to the GET request made to the tracker
    """
    def onSuccessfulConnection(self, responseBytes: bytes) -> Tuple[dict, List[Peer]]:
        responseAsByteArray: bytearray = bytearray(responseBytes)
        peersPartStartingPosition: int = responseAsByteArray.find(self.PEERS_PART_HEADER)
        peersPart: bytearray = responseAsByteArray[peersPartStartingPosition: -1]  # exclude a trailing 'e'
        nonPeersPart: dict = bdecode(responseAsByteArray.replace(peersPart, b""))
        return nonPeersPart, self.computePeers(peersPart)

    """
    Computes the peer list according to the torrent meta info file
    @:param announceURL - the URL of the tracker
    @:param infoHash - hash value of the "info" section in the torrent meta info file
    @:param totalSize - total size of the content
    @:return the list of peers received from the tracker
    """
    def getPeerList(self, announceURL: str, infoHash: bytes, totalSize: int) -> List[Peer]:
        payload = {
            self.PAYLOAD_INFO_HASH_KEY: infoHash,
            self.PAYLOAD_PEER_ID_KEY: self.PEER_ID,
            self.PAYLOAD_PORT_KEY: self.FIRST_AVAILABLE_PORT,
            self.PAYLOAD_UPLOADED_KEY: "0",
            self.PAYLOAD_DOWNLOADED_KEY: "0",
            self.PAYLOAD_LEFT_KEY: totalSize,
            self.PAYLOAD_COMPACT_KEY: 1,
            self.PAYLOAD_EVENT_KEY: self.PAYLOAD_EVENT_STARTED
        }

        while payload[self.PAYLOAD_PORT_KEY] <= self.LAST_AVAILABLE_PORT:
            for attempt in range(self.ATTEMPTS_TO_CONNECT_TO_TRACKER):
                print(f"""Trying to connect to tracker on port {payload[self.PAYLOAD_PORT_KEY]}, attempt {attempt + 1}/{self.ATTEMPTS_TO_CONNECT_TO_TRACKER}""")
                try:
                    response: Response = requests.get(announceURL, params=payload, timeout=self.REQUEST_ATTEMPT_TIMEOUT)
                    if response.status_code == self.SUCCESS_STATUS_CODE:
                        nonPeersPart, peerList = self.onSuccessfulConnection(response.content)
                        # nonPeersPart is not used right now, but it probably will be in the future
                        return peerList
                except Exception as e:
                    print("Error - ", e)
            payload[self.PAYLOAD_PORT_KEY] += 1  # try the next port

        print("Could not connect to the tracker")
        return []
