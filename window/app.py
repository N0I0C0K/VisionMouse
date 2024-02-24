import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # type: ignore

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # type: ignore

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)  # type: ignore

with open("style/style.qss.css", encoding="utf-8") as file:
    app.setStyleSheet(file.read())


def exec():
    window = MainWindow()
    window.show()
    app.exec_()
