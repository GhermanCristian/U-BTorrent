import asyncio
from typing import List, Final
import requests
from requests import Response
import utils
from domain.peer import Peer
from trackerResponseScanner import TrackerResponseScanner


class TrackerConnection:
    FIRST_AVAILABLE_PORT: Final[int] = 6881
    LAST_AVAILABLE_PORT: Final[int] = 6889
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"
    REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
    ATTEMPTS_TO_CONNECT_TO_TRACKER: Final[int] = 3
    ATTEMPTS_TO_GET_PEERS: Final[int] = 10
    WAITING_TIME_BETWEEN_GET_PEER_REQUESTS: Final[int] = 1  # seconds
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

    def __init__(self):
        self.__peerList: List[Peer] = []
        self.__host: Peer = Peer(0, 0)
        self.__currentIP: str = self.__getCurrentIP()

    def __getCurrentIP(self) -> str:
        return requests.get('https://api.ipify.org').content.decode('utf8')

    async def __getPeers(self, announceURL: str, payload: dict) -> bool:
        for _ in range(self.ATTEMPTS_TO_GET_PEERS):
            response: Response = requests.get(announceURL, params=payload, timeout=self.REQUEST_ATTEMPT_TIMEOUT)
            if response.status_code != self.SUCCESS_STATUS_CODE:
                return False
            nonPeersPart, self.__peerList = TrackerResponseScanner.scanTrackerResponse(response.content)
            response.close()
            self.__host = Peer(utils.convertIPFromStringToInt(self.__currentIP), payload[self.PAYLOAD_PORT_KEY])
            for peer in self.__peerList:
                if utils.convertIPFromIntToString(peer.IP) != self.__currentIP or (utils.convertIPFromIntToString(peer.IP) == self.__currentIP and not self.FIRST_AVAILABLE_PORT <= peer.port <= self.LAST_AVAILABLE_PORT):
                    return True
            await asyncio.sleep(self.WAITING_TIME_BETWEEN_GET_PEER_REQUESTS)
        return False

    """
    Makes a request to the specified tracker in order to obtain a list of peers.
    Additionally, the port on which the request is made (from the client side), is stored
    @:param announceURL - the URL of the tracker
    @:param infoHash - hash value of the "info" section in the torrent meta info file
    @:param totalSize - total size of the content that is downloaded / uploaded
    """
    async def makeTrackerRequest(self, announceURL: str, infoHash: bytes, totalSize: int) -> None:
        payload: dict = {
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
                try:
                    if await self.__getPeers(announceURL, payload):
                        return
                except Exception as e:
                    print("Error - ", e)
            payload[self.PAYLOAD_PORT_KEY] += 1  # try the next port
        # TODO - if the connection cannot be established with the current tracker address, try the others from the announceURL list

        self.__peerList.clear()

    @property
    def peerList(self) -> List[Peer]:
        return self.__peerList

    @property
    def host(self) -> Peer:
        return self.__host
