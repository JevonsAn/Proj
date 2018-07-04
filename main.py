import sys
from PyQt4 import QtGui
from views.myQtLib import MainWindow, LoginWindow



def main():
    app = QtGui.QApplication(sys.argv)

    l = LoginWindow()
    l.show()
    app.exec_()

    if l.success is True:
        # l.hide()
        w = MainWindow()
        w.show()

    else:
        sys.exit()
    # w.display_dataExport_uneven()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
