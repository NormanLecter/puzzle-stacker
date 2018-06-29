import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.uic import loadUi
from prompts_to_puzzle import resize_image, get_contours, prompt_location
from assemble_puzzle import try_to_assemble_puzzles
'''FUNKCJE I ZMIENNE DO DEBUGOWANIA'''


def catch_exceptions(t, val, tb):
    QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions
'''KONIEC FUNKCJI I ZMIENNYCH DO DEBUGOWANIA'''


def display_image(image):
    if len(image.shape) == 3:
        if(image.shape[2]) == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888
    img = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
    img = img.rgbSwapped()
    return img


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        loadUi('views/main.ui', self)
        self.prompt_button.setToolTip('Program pokazuje podpowiedzi na podstawie ułożonego obrazu')
        self.prompt_button.clicked.connect(self.open_prompt_window)
        self.solve_button.setToolTip('Program ułoży automatycznie puzzle')
        self.solve_button.clicked.connect(self.open_auto_solver_window)
        self.quit_button.setToolTip('Wyłączenie programu')
        self.quit_button.clicked.connect(QApplication.instance().quit)
        pixmap = QPixmap('views/logo.jpg')
        self.label.setPixmap(pixmap)

    def open_prompt_window(self):
        self.ui = PromptWindow()
        self.ui.show()
        self.hide()

    def open_auto_solver_window(self):
        self.ui = AutoSolverWindow()
        self.ui.show()
        self.hide()


class PromptWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('views/prompt.ui', self)
        self.images_load = False
        self.open_shuffle_button.setToolTip('Podaj zdjęcie z rozsypanymi puzzlami')
        self.open_shuffle_button.clicked.connect(self.file_open_shuffle)
        self.open_solved_button.setToolTip('Podaj zdjęcie z ułożonymi puzzlami')
        self.open_solved_button.clicked.connect(self.file_open_solved)
        self.back_button.setToolTip('Powrót do ekranu głównego')
        self.back_button.clicked.connect(self.open_main_window)
        self.next_button.setToolTip('Przejście do wybrania parametrów')
        self.next_button.clicked.connect(self.open_trackbars_window)
        pixmap = QPixmap('views/logo.jpg')
        self.solved_image.setPixmap(pixmap)
        pixmap = QPixmap('views/logo.jpg')
        self.shuffle_image.setPixmap(pixmap)

    def open_main_window(self):
        self.ui = Main()
        self.ui.show()
        self.hide()

    def open_trackbars_window(self):
        self.ui = TrackbarsWindow(self.path_to_shuffle_image, self.path_to_solved_image)
        self.ui.show()
        self.hide()

    def file_open_shuffle(self):
        options = QFileDialog.Options()
        self.path_to_shuffle_image, _ = QFileDialog.getOpenFileName(self, 'Podaj zdjęcie z rozsypanymi puzzlami', '',
                                                                    'Image files (*.jpg *.png)', options=options)
        if self.path_to_shuffle_image:
            image = display_image(resize_image(self.path_to_shuffle_image, 315, 215))
            pixmap = QPixmap(image)
            self.shuffle_image.setPixmap(pixmap)
            if self.images_load:
                self.next_button.setEnabled(True)
            else:
                self.images_load = True

    def file_open_solved(self):
        options = QFileDialog.Options()
        self.path_to_solved_image, _ = QFileDialog.getOpenFileName(self, 'Podaj zdjęcie z ułożonymi puzzlami', '',
                                                                   'Image files (*.jpg *.png)', options=options)
        if self.path_to_solved_image:
            image = display_image(resize_image(self.path_to_solved_image, 315, 215))
            pixmap = QPixmap(image)
            self.solved_image.setPixmap(pixmap)
            if self.images_load:
                self.next_button.setEnabled(True)
            else:
                self.images_load = True


class TrackbarsWindow(QWidget):
    def __init__(self, path_to_shuffle_image, path_to_solved_image):
        super().__init__()
        loadUi('views/trackbars.ui', self)
        self.path_to_shuffle_image = path_to_shuffle_image
        self.path_to_solved_image = path_to_solved_image
        self.min_slider.valueChanged.connect(self.value_change)
        self.max_slider.valueChanged.connect(self.value_change)
        self.back_button.setToolTip('Powrót do poprzedniego ekranu')
        self.back_button.clicked.connect(self.open_prompt_window)
        self.default_button.setToolTip('Przywróc ustawienia domyślne')
        self.default_button.clicked.connect(self.restore_default)
        self.next_button.setToolTip('Przejście do rozwiązania')
        self.next_button.clicked.connect(self.open_show_results)
        self.help_button.setToolTip('Pomoc dotycząca obługi okna')
        self.help_button.clicked.connect(self.open_help_window)
        self.value_change()

    def open_prompt_window(self):
        if self.path_to_solved_image is None:
            self.ui = AutoSolverWindow()
        else:
            self.ui = PromptWindow()
        self.ui.show()
        self.hide()

    def open_help_window(self):
        self.ui = HelpWindow()
        self.ui.show()

    def open_show_results(self):
        if self.path_to_solved_image is None:
            self.ui = ShowOneResult(self.contours, self.path_to_shuffle_image)
        else:
            self.ui = ShowResults(self.contours, self.path_to_solved_image, self.path_to_shuffle_image)
        self.ui.show()
        self.hide()

    def restore_default(self):
        self.min_slider.setValue(40)
        self.max_slider.setValue(70)

    def value_change(self):
        self.min_label.setText('Wartość min: ' + str(self.min_slider.value()))
        self.max_label.setText('Wartość maks: ' + str(self.max_slider.value()))
        self.contours, image = get_contours(self.path_to_shuffle_image, self.min_slider.value(),
                                            self.max_slider.value())
        pixmap = QPixmap(display_image(image))
        self.contour_image.setPixmap(pixmap)


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('views/help.ui', self)
        pixmap = QPixmap('views/threshold_good.jpg')
        self.good_image.setPixmap(pixmap)
        pixmap = QPixmap('views/threshold_bad.jpg')
        self.bad_image.setPixmap(pixmap)


class ShowResults(QWidget):
    def __init__(self, contours, path_to_solved_image, path_to_shuffle_image):
        super().__init__()
        loadUi('views/show_results.ui', self)
        self.path_to_shuffle_image = path_to_shuffle_image
        self.path_to_solved_image = path_to_solved_image
        self.back_button.setToolTip('Powrót do dostosowania parametrów')
        self.back_button.clicked.connect(self.open_trackbars_window)
        self.main_button.setToolTip('Powrót do menu głównego')
        self.main_button.clicked.connect(self.open_main_window)
        self.previous_button.setToolTip('Poprzedni obrazek')
        self.previous_button.clicked.connect(self.previous_image)
        self.next_button.setToolTip('Następny obrazek')
        self.next_button.clicked.connect(self.next_image)
        self.results = []
        self.position = 0
        self.prepare_result(contours)
        self.show_result(self.position)


    def open_trackbars_window(self):
        self.ui = TrackbarsWindow(self.path_to_shuffle_image, self.path_to_solved_image)
        self.ui.show()
        self.hide()

    def open_main_window(self):
        self.ui = Main()
        self.ui.show()
        self.hide()

    def previous_image(self):
        if self.position == 0:
            self.position = len(self.results) - 1
        else:
            self.position = self.position - 1
        self.show_result(self.position)

    def next_image(self):
        if self.position == len(self.results) - 1:
            self.position = 0
        else:
            self.position = self.position + 1
        self.show_result(self.position)

    def prepare_result(self, contours):
        images_with_prompt = prompt_location(self.path_to_shuffle_image, self.path_to_solved_image, contours)
        for image in images_with_prompt:
            image = resize_image(image, 340, 710)
            self.results.append(display_image(image))

    def show_result(self, index):
        pixmap = QPixmap(self.results[index])
        self.show_image.setPixmap(pixmap)


class AutoSolverWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('views/auto_solver.ui', self)
        self.open_shuffle_button.setToolTip('Podaj zdjęcie z rozsypanymi puzzlami')
        self.open_shuffle_button.clicked.connect(self.file_open_shuffle)
        self.back_button.setToolTip('Powrót do ekranu głównego')
        self.back_button.clicked.connect(self.open_main_window)
        self.next_button.setToolTip('Przejście do wybrania parametrów')
        self.next_button.clicked.connect(self.open_trackbars_window)
        pixmap = QPixmap('views/logo.jpg')
        self.solved_image.setPixmap(pixmap)
        pixmap = QPixmap('views/logo.jpg')
        self.shuffle_image.setPixmap(pixmap)

    def open_main_window(self):
        self.ui = Main()
        self.ui.show()
        self.hide()

    def open_trackbars_window(self):
        self.ui = TrackbarsWindow(self.path_to_shuffle_image, None)
        self.ui.show()
        self.hide()

    def file_open_shuffle(self):
        options = QFileDialog.Options()
        self.path_to_shuffle_image, _ = QFileDialog.getOpenFileName(self, 'Podaj zdjęcie z rozsypanymi puzzlami',
                                                                    '',
                                                                    'Image files (*.jpg *.png)', options=options)
        if self.path_to_shuffle_image:
            image = display_image(resize_image(self.path_to_shuffle_image, 315, 215))
            pixmap = QPixmap(image)
            self.shuffle_image.setPixmap(pixmap)
            self.next_button.setEnabled(True)


class ShowOneResult(QWidget):
    def __init__(self, contours, path_to_shuffle_image):
        super().__init__()
        loadUi('views/show_result.ui', self)
        self.contours = contours
        self.path_to_shuffle_image = path_to_shuffle_image
        self.back_button.setToolTip('Powrót do dostosowania parametrów')
        self.back_button.clicked.connect(self.open_trackbars_window)
        self.main_button.setToolTip('Powrót do menu głównego')
        self.main_button.clicked.connect(self.open_main_window)
        try:
            self.show_result()
        except IndexError:
            self.show_image.setText("Nie udało się ułożyć puzzli spróbuj zmienić wartość progowania lub powróć do menu "
                                    "głównego")
            self.open_main_window()

    def open_trackbars_window(self):
        self.ui = TrackbarsWindow(self.path_to_shuffle_image, None)
        self.ui.show()
        self.hide()

    def open_main_window(self):
        self.ui = Main()
        self.ui.show()
        self.hide()

    def show_result(self):
        self.show_image.setScaledContents(True)
        pixmap = QPixmap(display_image(try_to_assemble_puzzles(self.path_to_shuffle_image, self.contours)))
        self.show_image.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
