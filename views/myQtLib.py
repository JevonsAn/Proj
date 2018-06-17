import time
from PyQt4 import QtGui, QtCore
from views.views_setting import view_setting
from control.user_operation import add_user

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


class MyComboBox(QtGui.QComboBox):
    def __init__(self, items, parent=None):
        """
        :param items: 下拉菜单的内容
        :param parent:
        """
        QtGui.QComboBox.__init__(self, parent)
        width = view_setting['ComboBoxWidth']
        height = view_setting['ComboBOxHeight']
        self.resize(width, height)
        self.addItems(items)


# class MyCalendarWidget(QtGui.QCalendarWidget):
#     def __init__(self, parent=None):
#         QtGui.QCalendarWidget.__init__(self, parent)
#         self.hide

class MyDateEdit(QtGui.QDateEdit):
    def __init__(self, parent=None, date=None):
        QtGui.QDateEdit.__init__(self, parent)
        width = view_setting['ComboBoxWidth']
        height = view_setting['ComboBOxHeight']
        self.resize(width, height)
        self.setDate(QtCore.QDate.fromString(date, 'yyyy-MM-dd'))


class MyWidget(QtGui.QWidget):
    def __init__(self, parent=None, ):
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
        self.all_component = {}
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

        insert_weather = QtGui.QAction('天气资料', self)
        insert_weather.setStatusTip('天气资料')
        self.insert_weather_fuc()
        self.connect(insert_weather, QtCore.SIGNAL('triggered()'), self.display_insert_weather)
        data_menu.addAction(insert_weather)

    def create_user_fuc(self):
        create_user_component_list = []
        self.myLabel_userType = MyLabel("用户类型 : ", self)
        self.myLabel_userType.move(100, 60)
        create_user_component_list.append(self.myLabel_userType)

        self.myLineEdit_userType = MyLineEdit(self)
        self.myLineEdit_userType.move(200, 60)
        create_user_component_list.append(self.myLineEdit_userType)

        self.myLabel_userName = MyLabel("用户名称 : ", self)
        self.myLabel_userName.move(100, 120)
        create_user_component_list.append(self.myLabel_userName)

        self.myLineEdit_userName = MyLineEdit(self)
        self.myLineEdit_userName.move(200, 120)
        create_user_component_list.append(self.myLineEdit_userName)

        self.myLabel_gasUnit = MyLabel("气量单位 : ", self)
        self.myLabel_gasUnit.move(100, 180)
        create_user_component_list.append(self.myLabel_gasUnit)

        self.myLineEdit_gasUnit = MyLineEdit(self)
        self.myLineEdit_gasUnit.move(200, 180)
        create_user_component_list.append(self.myLineEdit_gasUnit)

        self.myLabel_userUnit = MyLabel("用户单位 : ", self)
        self.myLabel_userUnit.move(100, 240)
        create_user_component_list.append(self.myLabel_userUnit)

        self.myLineEdit_userUnit = MyLineEdit(self)
        self.myLineEdit_userUnit.move(200, 240)
        create_user_component_list.append(self.myLineEdit_userUnit)

        self.myLabel_beizhu = MyLabel("备注 : ", self)
        self.myLabel_beizhu.move(100, 300)
        create_user_component_list.append(self.myLabel_beizhu)

        self.myLineEdit_beizhu = MyLineEdit(self)
        self.myLineEdit_beizhu.move(200, 300)
        self.myLineEdit_beizhu.resize(400, 30)
        create_user_component_list.append(self.myLineEdit_beizhu)

        self.myButton_insertUser = MyButton("确认", self)
        self.myButton_insertUser.move(100, 360)
        create_user_component_list.append(self.myButton_insertUser)

        self.connect(self.myButton_insertUser, QtCore.SIGNAL("clicked()"), self.insert_user)

        self.all_component["create_user"] = create_user_component_list
        for x in create_user_component_list:
            x.hide()

    def insert_weather_fuc(self):
        insert_weather_component_list = []

        self.myLabel_date = MyLabel('日期：', self)
        self.myLabel_date.move(100, 60)
        insert_weather_component_list.append(self.myLabel_date)

        # self.myComboBox_date = MyComboBox(['1996/1/2', '1996/1/27'], self)
        # self.myComboBox_date.move(200, 60)
        # insert_weather_component_list.append(self.myComboBox_date)

        now_day = time.strftime("%Y-%m-%d", time.localtime())
        self.myDateEdit_date = MyDateEdit(self, now_day)
        self.myDateEdit_date.move(200, 60)
        insert_weather_component_list.append(self.myDateEdit_date)

        self.myLabel_maxTemperature = MyLabel('最高气温：', self)
        self.myLabel_maxTemperature.move(100, 120)
        insert_weather_component_list.append(self.myLabel_maxTemperature)

        self.myLineEdit_maxTemperature = MyLineEdit(self)
        self.myLineEdit_maxTemperature.move(200, 120)
        insert_weather_component_list.append(self.myLineEdit_maxTemperature)

        self.myLabel_maxTemperatureCentigrade = MyLabel('℃', self)
        self.myLabel_maxTemperatureCentigrade.move(300, 120)
        insert_weather_component_list.append(self.myLabel_maxTemperatureCentigrade)

        self.myLabel_minTemperature = MyLabel('最低气温：', self)
        self.myLabel_minTemperature.move(100, 180)
        insert_weather_component_list.append(self.myLabel_minTemperature)

        self.myLineEdit_minTemperature = MyLineEdit(self)
        self.myLineEdit_minTemperature.move(200, 180)
        insert_weather_component_list.append(self.myLineEdit_minTemperature)

        self.myLabel_minTemperatureCentigrade = MyLabel('℃', self)
        self.myLabel_minTemperatureCentigrade.move(300, 180)
        insert_weather_component_list.append(self.myLabel_minTemperatureCentigrade)

        self.myLabel_avgTemperature = MyLabel('平均气温：', self)
        self.myLabel_avgTemperature.move(100, 240)
        insert_weather_component_list.append(self.myLabel_avgTemperature)

        self.myLineEdit_avgTemperature = MyLineEdit(self)
        self.myLineEdit_avgTemperature.move(200, 240)
        insert_weather_component_list.append(self.myLineEdit_avgTemperature)

        self.myLabel_avgTemperatureCentigrade = MyLabel('℃', self)
        self.myLabel_avgTemperatureCentigrade.move(300, 240)
        insert_weather_component_list.append(self.myLabel_avgTemperatureCentigrade)

        self.myButton_insertWeather = MyButton("确认", self)
        self.myButton_insertWeather.move(100, 300)
        insert_weather_component_list.append(self.myButton_insertWeather)

        self.connect(self.myButton_insertWeather, QtCore.SIGNAL("clicked()"), self.insert_weather)

        self.all_component["insert_weather"] = insert_weather_component_list
        for x in insert_weather_component_list:
            x.hide()

    def display_create_user(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                x.hide()
        for x in self.all_component["create_user"]:
            x.show()

    def display_insert_weather(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                x.hide()
        for x in self.all_component['insert_weather']:
            x.show()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def insert_user(self):
        userType = self.myLineEdit_userType.text()
        userName = self.myLineEdit_userName.text()
        gasUnit = self.myLineEdit_gasUnit.text()
        userUnit = self.myLineEdit_userUnit.text()
        remark = self.myLineEdit_beizhu.text()
        if userUnit and userName and gasUnit and userType:
            res = add_user(userType, userName, gasUnit, userUnit)
            if res[0]:
                print("success")
            else:
                print(res[1])
        else:
            print("you can't")


    def insert_weather(self):
        date = self.myDateEdit_date.text()
        maxTemperature = self.myLineEdit_maxTemperature.text()
        minTemperature = self.myLineEdit_minTemperature.text()
        avgTemperature = self.myLineEdit_avgTemperature.text()
        if date and maxTemperature and minTemperature and avgTemperature:
            pass
        else:
            print("you can't")
            # ddd

