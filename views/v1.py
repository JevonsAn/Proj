import sys
from PyQt4 import QtGui
from views.myQtLib import MainWindow


def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

