from PyQt4 import QtGui, QtCore
from views.views_setting import view_setting


class MyButton(QtGui.QPushButton):
    def __init__(self, name, cl, tool_tip=""):
        """
            name: Button上的字
            cl：创建Button时需要的
            tool_tip: Button的提示框
        """
        QtGui.QPushButton.__init__(self, name, cl)
        width = view_setting["ButtonWidth"]
        height = view_setting["ButtonHeight"]
        self.resize(width, height)
        self.setToolTip(tool_tip)


class MyLabel(QtGui.QLabel):
    def __init__(self, name, cl):
        """
            name: Button上的字
            tool_tip: Button的提示框
        """
        QtGui.QLabel.__init__(self, name, cl)
        width = view_setting["ButtonWidth"]
        height = view_setting["ButtonHeight"]
        self.resize(width, height)


class MyLineEdit(QtGui.QLineEdit):
    def __init__(self, cl):
        """
            name: Button上的字
            cl：创建Button时需要的
            tool_tip: Button的提示框
        """
        QtGui.QLineEdit.__init__(self, cl)
        width = view_setting["ButtonWidth"]
        height = view_setting["ButtonHeight"]
        self.resize(width, height)


class MyWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.resize(1000, 600)
        # self.center()
        # self.move(450, 200)
        # self.setGeometry(300, 300, 250, 150)
        # self.setWindowTitle('用气指标软件')
        # self.setWindowIcon(QtGui.QIcon('../static/icons/icon0.jpg'))

        quit = MyButton('退出', self, '点击<br><b>退出</b>！')
        quit.move(100, 200)

        toolTipFont = QtGui.QFont('宋体', 10)
        QtGui.QToolTip.setFont(toolTipFont)
        # quit.setGeometry(100, 200, 80, 40)

        self.connect(quit, QtCore.SIGNAL('clicked()'), QtGui.qApp, QtCore.SLOT('quit()'))


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.all_zujian = {}
        width = view_setting["MainWindowWidth"]
        height = view_setting["MainWindowHeight"]
        self.resize(width, height)
        self.center()
        self.setWindowTitle('用气指标软件')
        self.setWindowIcon(QtGui.QIcon('../static/icons/icon0.jpg'))

        self.statusBar()

        menubar = self.menuBar()
        file = menubar.addMenu('&软件')
        signin_menu = menubar.addMenu('&登陆用户')
        user_menu = menubar.addMenu('&用户操作')
        data_menu = menubar.addMenu('&数据操作')
        yongqi_menu = menubar.addMenu('&用气指标')
        xishu_menu = menubar.addMenu('&不均匀系数')

        exit = QtGui.QAction('退出', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('退出软件')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        file.addAction(exit)

        create_user = QtGui.QAction('新建用户', self)
        create_user.setStatusTip('新建用户')
        self.create_user_fuc()
        self.connect(create_user, QtCore.SIGNAL('triggered()'), self.display_create_user)
        user_menu.addAction(create_user)

    def create_user_fuc(self):
        create_user_zujian_list = []
        self.myLabel_userType = MyLabel("用户类型 : ", self)
        self.myLabel_userType.move(100, 60)
        create_user_zujian_list.append(self.myLabel_userType)

        self.myLineEdit_userType = MyLineEdit(self)
        self.myLineEdit_userType.move(200, 60)
        create_user_zujian_list.append(self.myLineEdit_userType)

        self.myLabel_userName = MyLabel("用户名称 : ", self)
        self.myLabel_userName.move(100, 120)
        create_user_zujian_list.append(self.myLabel_userName)

        self.myLineEdit_userName = MyLineEdit(self)
        self.myLineEdit_userName.move(200, 120)
        create_user_zujian_list.append(self.myLineEdit_userName)

        self.myLabel_gasUnit = MyLabel("气量单位 : ", self)
        self.myLabel_gasUnit.move(100, 180)
        create_user_zujian_list.append(self.myLabel_gasUnit)

        self.myLineEdit_gasUnit = MyLineEdit(self)
        self.myLineEdit_gasUnit.move(200, 180)
        create_user_zujian_list.append(self.myLineEdit_gasUnit)

        self.myLabel_userUnit = MyLabel("用户单位 : ", self)
        self.myLabel_userUnit.move(100, 240)
        create_user_zujian_list.append(self.myLabel_userUnit)

        self.myLineEdit_userUnit = MyLineEdit(self)
        self.myLineEdit_userUnit.move(200, 240)
        create_user_zujian_list.append(self.myLineEdit_userUnit)

        self.myLabel_beizhu = MyLabel("备注 : ", self)
        self.myLabel_beizhu.move(100, 300)
        create_user_zujian_list.append(self.myLabel_beizhu)

        self.myLineEdit_beizhu = MyLineEdit(self)
        self.myLineEdit_beizhu.move(200, 300)
        self.myLineEdit_beizhu.resize(400, 30)
        create_user_zujian_list.append(self.myLineEdit_beizhu)

        self.myButton_insertUser = MyButton("确认", self)
        self.myButton_insertUser.move(100, 360)
        create_user_zujian_list.append(self.myButton_insertUser)

        def insert_user(cl):
            pass

        self.myButton_insertUser.connect(QtCore.SIGNAL("clicked()"), insert_user)


        self.all_zujian["create_user"] = create_user_zujian_list
        for x in create_user_zujian_list:
            x.hide()

    def display_create_user(self):
        for k in self.all_zujian:
            for x in self.all_zujian[k]:
                x.hide()
        for x in self.all_zujian["create_user"]:
            x.show()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
