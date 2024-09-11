import sys
import random
import pathlib

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog

HOME_DIR = str(pathlib.Path.home().absolute())


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QPushButton("Open File")
        # self.text = QLabel(text="Hello World", alignment=Qt.AlignCenter)
        # self.

        self.layout = QVBoxLayout(self)
        # self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        # self.text.setText(random.choice(self.hello))
        self.cb_open_file_dialog()

    def cb_open_file_dialog(self):
        file_name, file_type = QFileDialog.getOpenFileName(self, caption="Open Image", dir=HOME_DIR, filter="*.h5")
        print(file_name, file_type)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
