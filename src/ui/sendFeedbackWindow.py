from tkinter import Tk, Toplevel
from typing import Final


class SendFeedbackWindow:
    def __init__(self, mainWindow: Tk):
        self.__sendFeedbackWindow: Toplevel = self.__createSendFeedbackWindow(mainWindow)
        
    def __createSendFeedbackWindow(self, mainWindow: Tk) -> Toplevel:
        SEND_FEEDBACK_WINDOW_TITLE: Final[str] = "Send feedback"
        SEND_FEEDBACK_WINDOW_MIN_WIDTH_IN_PIXELS: Final[int] = 640
        SEND_FEEDBACK_WINDOW_MIN_HEIGHT_IN_PIXELS: Final[int] = 480

        sendFeedbackWindow: Toplevel = Toplevel()
        sendFeedbackWindow.title(SEND_FEEDBACK_WINDOW_TITLE)
        sendFeedbackWindow.minsize(SEND_FEEDBACK_WINDOW_MIN_WIDTH_IN_PIXELS, SEND_FEEDBACK_WINDOW_MIN_HEIGHT_IN_PIXELS)
        sendFeedbackWindow.transient(mainWindow)  # so that the window is not covered by the main window after exiting the directory dialog
        return sendFeedbackWindow
