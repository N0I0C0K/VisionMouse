from PyQt5.QtWidgets import QWidget
from qfluentwidgets import ScrollArea
from random import choices
import string


class HomeInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("".join(choices(string.printable, k=10)))
