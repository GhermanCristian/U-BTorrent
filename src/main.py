import threading
from service.torrentClient import TorrentClient
from ui.GUI import GUI


def main():
    torrentClient: TorrentClient = TorrentClient()
    thread = threading.Thread(target=torrentClient.start)
    userInterface: GUI = GUI(torrentClient)
    thread.start()
    userInterface.run()


if __name__ == "__main__":
    main()
