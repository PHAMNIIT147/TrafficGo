from PyQt5.QtWidgets import QApplication
import qdarkstyle
import sys
from src.views.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    win = MainWindow()

    app.setStyleSheet(qdarkstyle.load_stylesheet())
    # Show main window
    win.show()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()      