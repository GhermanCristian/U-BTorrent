import asyncio
from typing import List, Final, Dict, Any
import requests
from requests import Response
import utils
from domain.peer import Peer
from service.trackerResponseScanner import TrackerResponseScanner


class TrackerConnection:
    FIRST_AVAILABLE_PORT: Final[int] = 6881
    LAST_AVAILABLE_PORT: Final[int] = 6889
    PEER_ID: Final[str] = "ABCDEFGHIJKLMNOPQRST"

    def __init__(self):
        self.__peerList: List[Peer] = []
        self.__host: Peer = Peer()
        self.__currentIP: str = self.__getCurrentIP()
        self.__currentPort: int = self.FIRST_AVAILABLE_PORT

    def __getCurrentIP(self) -> str:
        URL: Final[str] = 'https://api.ipify.org'
        return requests.get(URL).content.decode('utf8')

    async def __getPeers(self, announceURL: str, payload: Dict[str, Any]) -> bool:
        REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
        WAITING_TIME_BETWEEN_GET_PEER_REQUESTS: Final[int] = 1  # seconds
        ATTEMPTS_TO_GET_PEERS: Final[int] = 10
        SUCCESS_STATUS_CODE: Final[int] = 200

        for _ in range(ATTEMPTS_TO_GET_PEERS):
            response: Response = requests.get(announceURL, params=payload, timeout=REQUEST_ATTEMPT_TIMEOUT)
            if response.status_code != SUCCESS_STATUS_CODE:
                return False
            nonPeersPart, self.__peerList = TrackerResponseScanner.scanTrackerResponse(response.content)
            response.close()
            self.__host = Peer(utils.convertIPFromStringToInt(self.__currentIP), self.__currentPort)
            for peer in self.__peerList:
                if utils.convertIPFromIntToString(peer.IP) != self.__currentIP or (utils.convertIPFromIntToString(peer.IP) == self.__currentIP and not self.FIRST_AVAILABLE_PORT <= peer.port <= self.LAST_AVAILABLE_PORT):
                    return True
            await asyncio.sleep(WAITING_TIME_BETWEEN_GET_PEER_REQUESTS)
        return False

    """
    Makes a request to the specified tracker in order to obtain a list of peers.
    Additionally, the port on which the request is made (from the client side), is stored
    @:param announceURL - the URL of the tracker
    @:param infoHash - hash value of the "info" section in the torrent meta info file
    @:param totalSize - total size of the content that is downloaded / uploaded
    """
    async def makeTrackerRequest(self, announceURL: str, infoHash: bytes, totalSize: int) -> None:
        ATTEMPTS_TO_CONNECT_TO_TRACKER: Final[int] = 3
        PAYLOAD: Final[Dict[str, Any]] = {
            "info_hash": infoHash,
            "peer_id": self.PEER_ID,
            "port": self.__currentPort,
            "uploaded": "0",
            "downloaded": "0",
            "left": totalSize,
            "compact": 1,
            "event": "started"
        }

        while self.__currentPort <= self.LAST_AVAILABLE_PORT:
            for attempt in range(ATTEMPTS_TO_CONNECT_TO_TRACKER):
                try:
                    if await self.__getPeers(announceURL, PAYLOAD):
                        return
                except Exception as e:
                    print("Error - ", e)
            self.__currentPort += 1
        # TODO - if the connection cannot be established with the current tracker address, try the others from the announceURL list

        self.__peerList.clear()

    @property
    def peerList(self) -> List[Peer]:
        return self.__peerList

    @property
    def host(self) -> Peer:
        return self.__host
