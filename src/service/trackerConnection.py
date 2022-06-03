import asyncio
from typing import List, Final, Dict, Any, Tuple, Callable
import requests
from requests import Response
import utils
from domain.peer import Peer
from service.torrentMetaInfoScanner import TorrentMetaInfoScanner
from service.trackerResponseScanner import TrackerResponseScanner


class TrackerConnection:
    FIRST_AVAILABLE_PORT: Final[int] = 6881
    LAST_AVAILABLE_PORT: Final[int] = 6889
    PORT_KEY: Final[str] = "port"

    def __init__(self, scanner: TorrentMetaInfoScanner):
        self.__announceURL: str = scanner.announceURL
        self.__infoHash: bytes = scanner.infoHash
        self.__totalSize: int = scanner.getTotalContentSize()
        self.__currentIP: str = self.__getCurrentIP()

    def __getCurrentIP(self) -> str:
        URL: Final[str] = 'https://api.ipify.org'
        return requests.get(URL).content.decode('utf8')

    async def __getPeers(self, payload: Dict[str, Any]) -> List[Peer] | None:
        REQUEST_ATTEMPT_TIMEOUT: Final[int] = 30  # seconds
        WAITING_TIME_BETWEEN_GET_PEER_REQUESTS: Final[int] = 1  # seconds
        ATTEMPTS_TO_GET_PEERS: Final[int] = 10
        SUCCESS_STATUS_CODE: Final[int] = 200

        for _ in range(ATTEMPTS_TO_GET_PEERS):
            response: Response = requests.get(self.__announceURL, params=payload, timeout=REQUEST_ATTEMPT_TIMEOUT)
            if response.status_code != SUCCESS_STATUS_CODE:
                return None
            nonPeersPart, peerList = TrackerResponseScanner.scanTrackerResponse(response.content)
            response.close()
            for peer in peerList:
                if utils.convertIPFromIntToString(peer.IP) != self.__currentIP or (utils.convertIPFromIntToString(peer.IP) == self.__currentIP and not self.FIRST_AVAILABLE_PORT <= peer.port <= self.LAST_AVAILABLE_PORT):
                    return peerList
            await asyncio.sleep(WAITING_TIME_BETWEEN_GET_PEER_REQUESTS)

    def __getStartedPayloadForPort(self, port: int) -> Dict[str, bytes | str | int]:
        return {
            "info_hash": self.__infoHash,
            "peer_id": utils.PEER_ID,
            "port": port,
            "uploaded": "0",
            "downloaded": "0",
            "left": self.__totalSize,
            "compact": 1,
            "event": "started"
        }

    def __getFinishedPayloadForPort(self, port: int) -> Dict[str, bytes | str | int]:
        return {
            "info_hash": self.__infoHash,
            "peer_id": utils.PEER_ID,
            "port": port,
            "uploaded": "0",
            "downloaded": self.__totalSize,
            "left": "0",
            "compact": 1,
            "event": "finished"
        }

    async def __makeRequest(self, payloadGetter: Callable[[int], Dict[str, bytes | str | int]]) -> Tuple[List[Peer], int]:
        ATTEMPTS_TO_CONNECT_TO_TRACKER: Final[int] = 3

        currentPort: int = self.FIRST_AVAILABLE_PORT
        while currentPort <= self.LAST_AVAILABLE_PORT:
            for attempt in range(ATTEMPTS_TO_CONNECT_TO_TRACKER):
                try:
                    peerList: List[Peer] | None = await self.__getPeers(payloadGetter(currentPort))
                    if peerList is not None:
                        return peerList, currentPort
                except Exception as e:
                    print("Error - ", e)
            currentPort += 1
        # TODO - if the connection cannot be established with the current tracker address, try the others from the announceURL list

    async def makeTrackerStartedRequest(self) -> Tuple[List[Peer], int]:
        return await self.__makeRequest(lambda currentPort: self.__getStartedPayloadForPort(currentPort))

    async def makeTrackerFinishedRequest(self) -> Tuple[List[Peer], int]:
        return await self.__makeRequest(lambda currentPort: self.__getFinishedPayloadForPort(currentPort))

    @property
    def currentIP(self) -> str:
        return self.__currentIP
