import sys
from PyQt4 import QtGui, QtCore
from views.views_setting import setting


def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


class myButton(QtGui.QPushButton):
    def __init__(self, name, cl, tool_tip):
        """
            name: Button上的字
            cl：创建Button时需要的
            tool_tip: Button的提示框
        """
        QtGui.QPushButton.__init__(self, name, cl)
        width = setting["ButtonWidth"]
        height = setting["ButtonHeight"]
        self.resize(width, height)
        self.setToolTip(tool_tip)


class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.resize(1000, 600)
        self.center()
        # self.move(450, 200)
        # self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('用气指标软件')
        self.setWindowIcon(QtGui.QIcon('../static/icons/icon0.jpg'))

        quit = myButton('退出', self, '点击<br><b>退出</b>！')
        quit.move(100, 200)

        toolTipFont = QtGui.QFont('宋体', 10)
        QtGui.QToolTip.setFont(toolTipFont)
        # quit.setGeometry(100, 200, 80, 40)

        self.connect(quit, QtCore.SIGNAL('clicked()'), QtGui.qApp, QtCore.SLOT('quit()'))

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)








if __name__ == '__main__':
    main()

