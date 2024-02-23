from qfluentwidgets import FluentWindow, FluentIcon as Icon
from .interface import HomeInterface


class MainWindow(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initWindow()
        self.initNavigation()

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowTitle("Vision Mouse")

        self.setMicaEffectEnabled(True)

    def initNavigation(self):
        self.addSubInterface(HomeInterface(self), Icon.HOME, "Home")
        self.addSubInterface(HomeInterface(self), Icon.HOME, "Home1")
