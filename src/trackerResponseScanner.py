from typing import List, Final, Tuple
from bencode3 import bdecode
from domain.peer import Peer


class TrackerResponseScanner:
    PEERS_PART_HEADER: Final[bytes] = b"5:peers"
    PEER_SIZE: Final[int] = 6  # bytes

    """
    Determines the list of peers from the tracker response
    @:param peersPart - a bytearray containing some headers and the extended ASCII-encoded values representing the IP:port of the peers
    The header starts with "5:peers" - part of the bencode standard, then a decimal number = the number of bytes needed for the IPs and ports, which is followed by a colon.
    The decimal number has to be a multiple of 6 (4 bytes for each IP, 2 for each port)
    @:return a list of Peer objects, extracted from the input
    """
    @staticmethod
    def computePeers(peersPart: bytearray) -> List[Peer]:
        peerAddressList: List[Peer] = []
        currentIndex: int = len(TrackerResponseScanner.PEERS_PART_HEADER)  # skip the "5:peers" part
        peersByteCount: int = 0  # the number of bytes used to represent peer addresses

        while 48 + 0 <= peersPart[currentIndex] <= 48 + 9:
            peersByteCount = peersByteCount * 10 + peersPart[currentIndex] - 48
            currentIndex += 1
        currentIndex += 1  # skip the ":"
        assert peersByteCount % TrackerResponseScanner.PEER_SIZE == 0, f"The number of bytes for the peers IPs and ports should be a multiple of {TrackerResponseScanner.PEER_SIZE}"

        for _ in range(0, peersByteCount // TrackerResponseScanner.PEER_SIZE):
            currentIP = peersPart[currentIndex] * 256**3 + peersPart[currentIndex + 1] * 256**2 + peersPart[currentIndex + 2] * 256 + peersPart[currentIndex + 3]
            currentPort = peersPart[currentIndex + 4] * 256 + peersPart[currentIndex + 5]
            peerAddressList.append(Peer(currentIP, currentPort))
            currentIndex += TrackerResponseScanner.PEER_SIZE

        return peerAddressList

    """
    Processes the tracker response
    @:param responseBytes - the response to the GET request made to the tracker
    """
    @staticmethod
    def scanTrackerResponse(responseBytes: bytes) -> Tuple[dict, List[Peer]]:
        responseAsByteArray: bytearray = bytearray(responseBytes)
        peersPartStartingPosition: int = responseAsByteArray.find(TrackerResponseScanner.PEERS_PART_HEADER)
        peersPart: bytearray = responseAsByteArray[peersPartStartingPosition: -1]  # exclude a trailing 'e'
        nonPeersPart: dict = bdecode(responseAsByteArray.replace(peersPart, b""))
        return nonPeersPart, TrackerResponseScanner.computePeers(peersPart)
