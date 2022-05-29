from typing import List, Final, Tuple
from bencode3 import bdecode
import utils
from domain.peer import Peer


class TrackerResponseScanner:
    PEERS_PART_HEADER: Final[bytes] = b"5:peers"

    """
    Determines the list of peers from the tracker response
    @:param peersPart - a bytearray containing some headers and the extended ASCII-encoded values representing the IP:port of the peers
    The header starts with "5:peers" - part of the bencode standard, then a decimal number = the number of bytes needed for the IPs and ports, which is followed by a colon.
    The decimal number has to be a multiple of 6 (4 bytes for each IP, 2 for each port)
    @:return a list of Peer objects, extracted from the input
    """
    @staticmethod
    def __computePeersBinaryModel(peersPart: bytearray) -> List[Peer]:
        ZERO_DIGIT_ASCII_VALUE: Final[int] = 48
        NINE_DIGIT_ASCII_VALUE: Final[int] = 57
        PEER_SIZE_BINARY_MODEL: Final[int] = 6  # bytes
        
        peerAddressList: List[Peer] = []
        currentIndex: int = len(TrackerResponseScanner.PEERS_PART_HEADER)  # skip the "5:peers" part
        peersByteCount: int = 0  # the number of bytes used to represent peer addresses

        while ZERO_DIGIT_ASCII_VALUE <= peersPart[currentIndex] <= NINE_DIGIT_ASCII_VALUE:
            peersByteCount = peersByteCount * 10 + peersPart[currentIndex] - ZERO_DIGIT_ASCII_VALUE
            currentIndex += 1
        currentIndex += 1  # skip the ":"
        assert peersByteCount % PEER_SIZE_BINARY_MODEL == 0, f"The number of bytes for the peers IPs and ports should be a multiple of {PEER_SIZE_BINARY_MODEL}"

        for _ in range(0, peersByteCount // PEER_SIZE_BINARY_MODEL):
            currentIP = peersPart[currentIndex] * 256**3 + peersPart[currentIndex + 1] * 256**2 + peersPart[currentIndex + 2] * 256 + peersPart[currentIndex + 3]
            currentPort = peersPart[currentIndex + 4] * 256 + peersPart[currentIndex + 5]
            peerAddressList.append(Peer(currentIP, currentPort))
            currentIndex += PEER_SIZE_BINARY_MODEL

        return peerAddressList

    @staticmethod
    def __scanTrackerResponseBinaryModel(responseBytes: bytes) -> Tuple[dict, List[Peer]]:
        responseAsByteArray: bytearray = bytearray(responseBytes)
        peersPartStartingPosition: int = responseAsByteArray.find(TrackerResponseScanner.PEERS_PART_HEADER)
        peersPart: bytearray = responseAsByteArray[peersPartStartingPosition: -1]  # exclude a trailing 'e'
        nonPeersPart: dict = bdecode(responseAsByteArray.replace(peersPart, b""))
        return nonPeersPart, TrackerResponseScanner.__computePeersBinaryModel(peersPart)

    @staticmethod
    def __scanTrackerResponseDictionaryModel(responseBytes: bytes) -> Tuple[dict, List[Peer]]:
        PEERS_DICT_KEY: Final[str] = "peers"
        PEER_IP_KEY_DICT_MODEL: Final[str] = "ip"
        PEER_PORT_KEY_DICT_MODEL: Final[str] = "port"

        decoded: dict = bdecode(responseBytes)
        peerList: List[Peer] = [Peer(utils.convertIPFromStringToInt(peer[PEER_IP_KEY_DICT_MODEL]), peer[PEER_PORT_KEY_DICT_MODEL])
                                for peer in decoded[PEERS_DICT_KEY]]
        decoded.pop(PEERS_DICT_KEY)
        return decoded, peerList

    """
    Processes the tracker response
    @:param responseBytes - the response to the GET request made to the tracker
    """
    @staticmethod
    def scanTrackerResponse(responseBytes: bytes) -> Tuple[dict, List[Peer]]:
        DICT_MODEL_IDENTIFIER: Final[bytes] = b"5:peersld2:ip"

        if responseBytes.find(DICT_MODEL_IDENTIFIER) != -1:
            return TrackerResponseScanner.__scanTrackerResponseDictionaryModel(responseBytes)
        return TrackerResponseScanner.__scanTrackerResponseBinaryModel(responseBytes)
