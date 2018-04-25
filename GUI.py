import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QFormLayout, QSlider
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import *


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Puzzle Stacker'
        self.left = 100
        self.top = 100
        self.width = 500
        self.height = 500
        self.fbox = QFormLayout()
        self.image_load = False
        self.initUI()

    def initUI(self):
        self.clearLayout(self.fbox)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        button_hint = QPushButton('Podpowiadarka', self)
        button_hint.clicked.connect(self.hintUI)
        button_quit = QPushButton('Zakończ', self)
        button_quit.setToolTip('Wyłączenie programu')
        button_quit.clicked.connect(QApplication.instance().quit)
        self.fbox.addRow(button_hint)
        self.fbox.addRow(button_quit)
        self.setLayout(self.fbox)
        self.show()


    def hintUI(self):
        self.clearLayout(self.fbox)
        self.image_load = False
        self.shuffle_image = QLabel(self)
        self.solved_image = QLabel(self)
        self.fbox.addRow(self.shuffle_image, self.solved_image)
        button_open_shuffle = QPushButton('Rozsypane puzzle', self)
        button_open_shuffle.setToolTip('Podaj zdjęcie z rozsypanymi puzzlami')
        button_open_shuffle.clicked.connect(self.file_open_shuffle)
        button_open_solved = QPushButton('Ułożone puzzle', self)
        button_open_solved.setToolTip('Podaj zdjęcie z ułożonymi puzzlami')
        button_open_solved.clicked.connect(self.file_open_solved)
        self.fbox.addRow(button_open_shuffle, button_open_solved)
        button_return = QPushButton('Powrót', self)
        button_return.setToolTip('Powrót do ekranu głównego')
        button_return.clicked.connect(self.initUI)
        self.button_next = QPushButton('Dalej', self)
        self.button_next.setToolTip('Przejście do wybrania parametrów')
        self.button_next.setEnabled(False)
        self.button_next.clicked.connect(self.contoursUI)
        self.fbox.addRow(button_return, self.button_next)
        self.setLayout(self.fbox)
        self.show()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def file_open_shuffle(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Podaj zdjęcie z rozsypanymi puzzlami", "",
                                                  "Image files (*.jpg)", options=options)
        if fileName:
            pixmap = QPixmap(fileName)
            self.shuffle_image.setPixmap(pixmap)
            if self.image_load == True:
                self.button_next.setEnabled(True)
            else:
                self.image_load = True

    def file_open_solved(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Podaj zdjęcie z ułożonymi puzzlami", "",
                                                  "Image files (*.jpg)", options=options)
        if fileName:
            pixmap = QPixmap(fileName)
            self.solved_image.setPixmap(pixmap)
            if self.image_load == True:
                self.button_next.setEnabled(True)
            else:
                self.image_load = True

    def contoursUI(self):
        self.clearLayout(self.fbox)
        self.threshold1 = QLabel("0")
        self.fbox.addRow(self.threshold1)
        self.slider_threshold1 = QSlider(Qt.Horizontal)
        self.slider_threshold1.setMinimum(0)
        self.slider_threshold1.setMaximum(255)
        self.slider_threshold1.setValue(0)
        self.slider_threshold1.setTickPosition(QSlider.TicksBelow)
        self.slider_threshold1.setTickInterval(1)
        self.slider_threshold1.valueChanged.connect(self.valuechange)
        self.fbox.addRow(self.slider_threshold1)
        self.threshold2 = QLabel("0")
        self.fbox.addRow(self.threshold2)
        self.slider_threshold2 = QSlider(Qt.Horizontal)
        self.slider_threshold2.setMinimum(0)
        self.slider_threshold2.setMaximum(255)
        self.slider_threshold2.setValue(0)
        self.slider_threshold2.setTickPosition(QSlider.TicksBelow)
        self.slider_threshold2.setTickInterval(1)
        self.slider_threshold2.valueChanged.connect(self.valuechange)
        self.fbox.addRow(self.slider_threshold2)
        self.setLayout(self.fbox)
        self.show()

    def valuechange(self):
        self.threshold1.setText(str(self.slider_threshold1.value()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())