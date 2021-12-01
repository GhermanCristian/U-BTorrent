import unittest
from domain.peer import Peer
from trackerConnection import TrackerConnection


class TestTrackerConnection(unittest.TestCase):
    def setUp(self) -> None:
        self.__trackerConnection = TrackerConnection()

    def test_computePeers_ValidPeersPart_CorrectPeerList(self) -> None:
        self.assertEqual(self.__trackerConnection.computePeers("5:peers6:¼xá"), [Peer(3155919480, 6881)])

    def test_onSuccessfulConnection_ValidContent_CorrectNonPeerContent(self) -> None:
        nonPeersPart, _ = self.__trackerConnection.onSuccessfulConnection("d8:completei0e10:downloadedi0e10:incompletei1e8:intervali1720e12:min intervali860e5:peers6:¼xáe")
        self.assertEqual(nonPeersPart, {"complete": 0, "downloaded": 0, "incomplete": 1, "interval": 1720, "min interval": 860})

    def test_onSuccessfulConnection_ValidContent_CorrectPeerList(self) -> None:
        _, peerList = self.__trackerConnection.onSuccessfulConnection("d8:completei0e10:downloadedi0e10:incompletei1e8:intervali1720e12:min intervali860e5:peers6:¼xáe")
        self.assertEqual(peerList, [Peer(3155919480, 6881)])


if __name__ == '__main__':
    unittest.main()
