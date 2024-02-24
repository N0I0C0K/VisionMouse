from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea
from random import choices
import string


class HomeInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomeInterface")
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.initWindow()

    def initWindow(self):
        self.view.setObjectName("view")
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        home_label = QLabel("Vision Mouse", self.view)
