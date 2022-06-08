from tkinter import Toplevel, Tk, Label
from typing import Final, Literal, List
from ui import utilsGUI


class HelpWindow:
    FONT_SIZE: Final[int] = 14
    CENTER_ANCHOR: Final[Literal["center"]] = "center"
    X_PADDING: Final[int] = 20
    Y_PADDING: Final[int] = 20

    def __init__(self, mainWindow: Tk):
        self.__helpWindow: Toplevel = self.__createHelpWindow(mainWindow)
        self.__displayText()

    def __createHelpWindow(self, mainWindow: Tk) -> Toplevel:
        HELP_WINDOW_TITLE: Final[str] = "Help"
        HELP_WINDOW_MIN_WIDTH_IN_PIXELS: Final[int] = 960
        HELP_WINDOW_MIN_HEIGHT_IN_PIXELS: Final[int] = 560

        helpWindow: Toplevel = Toplevel()
        helpWindow.title(HELP_WINDOW_TITLE)
        helpWindow.minsize(HELP_WINDOW_MIN_WIDTH_IN_PIXELS, HELP_WINDOW_MIN_HEIGHT_IN_PIXELS)
        helpWindow.transient(mainWindow)  # so that the window is not covered by the main window after exiting the directory dialog
        return helpWindow

    def __displayText(self) -> None:
        content: Final[List[str]] = [
            "Peer = user involved in downloading / uploading a torrent",
            "Seeding = uploading a torrent",
            "Seed ratio = ratio between the amount of data uploaded and downloaded; the higher, the better",
            "Tracker = server which knows about all the peers for a download (it doesn't host any of the files though)",
            "\n",
            "Q: My torrent download doesn't start / Elapsed Time is stuck at 0, what do I do ?",
            "A: Most probably it's stuck trying to connect to peers - but perhaps there are none. Either wait some more or restart the program.",
            "It's also possible that you cannot connect to the tracker because it's private and your access is denied. Tough luck!"
            "\n",
            "Q: Uploading doesn't work, how to fix it ?",
            "A: It's possible all the peers already have the torrent, so there's no one to upload to. It might help to pause and resume the upload",
            "after a while, maybe some new peers have joined."
            "\n",
            "Q: After pausing a download / upload, the download / upload speed doesn't go straight to 0. Is it normal ?",
            "A: Yes. There's a short delay before the pause comes into effect, during which some data might still be downloaded / uploaded.",
            "\n",
            "Q: The torrent downloads too slowly, what can I do about it ?",
            "A: Maybe there aren't enough peers, or maybe your device or internet connection is not powerful enough to support high download speeds.",
            "If the problem persists, try closing any other programs that use up the network or the CPU."
        ]
        Label(self.__helpWindow,
              text="\n".join(content),
              font=(utilsGUI.FONT_NAME, self.FONT_SIZE)).pack(
                    padx=self.X_PADDING,
                    pady=self.Y_PADDING)
