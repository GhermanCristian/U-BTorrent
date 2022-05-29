from service.torrentClient import TorrentClient
from ui.GUI import GUI


def main():
    torrentClient: TorrentClient = TorrentClient()
    userInterface: GUI = GUI(torrentClient.singleTorrentProcessors)
    torrentClient.addObserver(userInterface)
    userInterface.run()


if __name__ == "__main__":
    main()
