from qfluentwidgets import FluentWindow, FluentIcon as Icon
from .interface import HomeInterface


class MainWindow(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainWindow")
        self.initWindow()
        self.initNavigation()
        # self.load_style()

    def load_style(self):
        with open("style/style.qss.css", encoding="utf-8") as file:
            self.setStyleSheet(file.read())

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowTitle("Vision Mouse")

        self.navigationInterface.setAcrylicEnabled(True)
        self.setMicaEffectEnabled(True)

    def initNavigation(self):
        self.addSubInterface(HomeInterface(self), Icon.HOME, "Home")
