from typing import List, Final
import requests
from requests import Response
from domain.peer import Peer
from trackerResponseScanner import TrackerResponseScanner


class TrackerConnection:
    FIRST_AVAILABLE_PORT: Final[int] = 6881
    LAST_AVAILABLE_PORT: Final[int] = 6889
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"
    REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
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
                        nonPeersPart, peerList = TrackerResponseScanner.scanTrackerResponse(response.content)
                        # nonPeersPart is not used right now, but it probably will be in the future
                        return peerList
                except Exception as e:
                    print("Error - ", e)
            payload[self.PAYLOAD_PORT_KEY] += 1  # try the next port

        print("Could not connect to the tracker")
        return []
