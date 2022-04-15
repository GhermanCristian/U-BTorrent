import unittest
from domain.peer import Peer
from trackerResponseScanner import TrackerResponseScanner


class TestTrackerResponseScanner(unittest.TestCase):
    def test_scanTrackerResponse_ValidContent_CorrectNonPeerContent(self) -> None:
        nonPeersPart, _ = TrackerResponseScanner.scanTrackerResponse(b'd8:completei0e10:downloadedi0e10:incompletei1e8:intervali1634e12:min intervali817e5:peers6:\xbc\x1b\x84\x08\x1a\xe1e')
        self.assertEqual(nonPeersPart, {"complete": 0, "downloaded": 0, "incomplete": 1, "interval": 1634, "min interval": 817})

    def test_scanTrackerResponse_ValidContent_CorrectPeerList(self) -> None:
        _, peerList = TrackerResponseScanner.scanTrackerResponse(b'd8:completei0e10:downloadedi0e10:incompletei1e8:intervali1634e12:min intervali817e5:peers6:\xbc\x1b\x84\x08\x1a\xe1e')
        self.assertEqual(peerList, [Peer(3155919880, 6881)])


if __name__ == '__main__':
    unittest.main()
