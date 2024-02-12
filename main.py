# main.py
from PyQt5.QtWidgets import QApplication
from main_application import MainApplication
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainApplication()
    mainWindow.show()
    sys.exit(app.exec_())
