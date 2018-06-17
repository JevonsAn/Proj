import time
from PyQt4 import QtGui, QtCore
from views.views_setting import view_setting
from control.user_operation import add_user, get_all_userType, get_userNames_by_userType

from control.user_operation import add_weather, datetime_to_timestamp
from pymysql import IntegrityError


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

        change_user = QtGui.QAction('编辑用户', self)
        change_user.setStatusTip('编辑用户')
        self.change_user_fuc()
        self.connect(change_user, QtCore.SIGNAL('triggered()'), self.display_change_user)
        user_menu.addAction(change_user)

        insert_weather = QtGui.QAction('录入天气', self)
        insert_weather.setStatusTip('录入天气')
        self.insert_weather_fuc()
        self.connect(insert_weather, QtCore.SIGNAL('triggered()'), self.display_insert_weather)
        data_menu.addAction(insert_weather)

    def create_user_fuc(self):
        create_user_component_dict = {}
        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 60)
        create_user_component_dict['myLabel_userType'] = myLabel_userType

        myLineEdit_userType = MyLineEdit(self)
        myLineEdit_userType.move(200, 60)
        create_user_component_dict['myLineEdit_userType'] = myLineEdit_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 120)
        create_user_component_dict['myLabel_userName'] = myLabel_userName

        myLineEdit_userName = MyLineEdit(self)
        myLineEdit_userName.move(200, 120)
        create_user_component_dict['myLineEdit_userName'] = myLineEdit_userName

        myLabel_gasUnit = MyLabel("气量单位 : ", self)
        myLabel_gasUnit.move(100, 180)
        create_user_component_dict['myLabel_gasUnit'] = myLabel_gasUnit

        myLineEdit_gasUnit = MyLineEdit(self)
        myLineEdit_gasUnit.move(200, 180)
        create_user_component_dict['myLineEdit_gasUnit'] = myLineEdit_gasUnit

        myLabel_userUnit = MyLabel("用户单位 : ", self)
        myLabel_userUnit.move(100, 240)
        create_user_component_dict['myLabel_userUnit'] = myLabel_userUnit

        myLineEdit_userUnit = MyLineEdit(self)
        myLineEdit_userUnit.move(200, 240)
        create_user_component_dict['myLineEdit_userUnit'] = myLineEdit_userUnit

        myLabel_beizhu = MyLabel("备注 : ", self)
        myLabel_beizhu.move(100, 300)
        create_user_component_dict['myLabel_beizhu'] = myLabel_beizhu

        myLineEdit_beizhu = MyLineEdit(self)
        myLineEdit_beizhu.move(200, 300)
        myLineEdit_beizhu.resize(400, 30)
        create_user_component_dict['myLineEdit_beizhu'] = myLineEdit_beizhu

        myButton_insertUser = MyButton("确认", self)
        myButton_insertUser.move(100, 360)
        create_user_component_dict['myButton_insertUser'] = myButton_insertUser

        self.connect(create_user_component_dict['myButton_insertUser'], QtCore.SIGNAL("clicked()"), self.insert_user)

        self.all_component["create_user"] = create_user_component_dict
        for x in create_user_component_dict:
            create_user_component_dict[x].hide()

    def change_user_fuc(self):
        change_user_component_dict = {}
        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 60)
        change_user_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        change_user_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 120)
        change_user_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 120)
        change_user_component_dict["myComboBox_userName"] = myComboBox_userName

        myButton_insertUser = MyButton("确认", self)
        myButton_insertUser.move(100, 360)
        change_user_component_dict["myButton_insertUser"] = myButton_insertUser

        self.all_component["change_user"] = change_user_component_dict
        for x in change_user_component_dict:
            change_user_component_dict[x].hide()

    def selectionchange(self):
        sender = self.sender()
        print(sender)
        for i in range(self.all_component["change_user"]["myComboBox_userName"].count()):
            self.all_component["change_user"]["myComboBox_userName"].removeItem(i)

        now_userType = sender.itemText(sender.currentIndex())
        userNames = get_userNames_by_userType(now_userType)
        self.all_component["change_user"]["myComboBox_userName"].addItems(userNames)

    def insert_weather_fuc(self):
        insert_weather_component_dict = {}

        myLabel_date = MyLabel('日期：', self)
        myLabel_date.move(100, 60)
        insert_weather_component_dict['myLabel_date'] = myLabel_date

        now_day = time.strftime("%Y-%m-%d", time.localtime())
        myDateEdit_date = MyDateEdit(self, now_day)
        myDateEdit_date.move(200, 60)
        insert_weather_component_dict['myDateEdit_date'] = myDateEdit_date

        myLabel_maxTemperature = MyLabel('最高气温：', self)
        myLabel_maxTemperature.move(100, 120)
        insert_weather_component_dict['myLabel_maxTemperature'] = myLabel_maxTemperature

        myLineEdit_maxTemperature = MyLineEdit(self)
        myLineEdit_maxTemperature.move(200, 120)
        insert_weather_component_dict['myLineEdit_maxTemperature'] = myLineEdit_maxTemperature

        myLabel_maxTemperatureCentigrade = MyLabel('℃', self)
        myLabel_maxTemperatureCentigrade.move(300, 120)
        insert_weather_component_dict['myLabel_maxTemperatureCentigrade'] = myLabel_maxTemperatureCentigrade

        myLabel_minTemperature = MyLabel('最低气温：', self)
        myLabel_minTemperature.move(100, 180)
        insert_weather_component_dict['myLabel_minTemperature'] = myLabel_minTemperature

        myLineEdit_minTemperature = MyLineEdit(self)
        myLineEdit_minTemperature.move(200, 180)
        insert_weather_component_dict['myLineEdit_minTemperature'] = myLineEdit_minTemperature

        myLabel_minTemperatureCentigrade = MyLabel('℃', self)
        myLabel_minTemperatureCentigrade.move(300, 180)
        insert_weather_component_dict['myLabel_minTemperatureCentigrade'] = myLabel_minTemperatureCentigrade

        myLabel_avgTemperature = MyLabel('平均气温：', self)
        myLabel_avgTemperature.move(100, 240)
        insert_weather_component_dict['myLabel_avgTemperature'] = myLabel_avgTemperature

        myLineEdit_avgTemperature = MyLineEdit(self)
        myLineEdit_avgTemperature.move(200, 240)
        insert_weather_component_dict['myLineEdit_avgTemperature'] = myLineEdit_avgTemperature

        myLabel_avgTemperatureCentigrade = MyLabel('℃', self)
        myLabel_avgTemperatureCentigrade.move(300, 240)
        insert_weather_component_dict['myLabel_avgTemperatureCentigrade'] = myLabel_avgTemperatureCentigrade

        myButton_insertWeather = MyButton("确认", self)
        myButton_insertWeather.move(100, 300)
        insert_weather_component_dict['myButton_insertWeather'] = myButton_insertWeather

        self.connect(insert_weather_component_dict['myButton_insertWeather'], QtCore.SIGNAL("clicked()"), self.insert_weather)

        self.all_component["insert_weather"] = insert_weather_component_dict
        for x in insert_weather_component_dict:
            insert_weather_component_dict[x].hide()

    def insert_user_data_fuc(self):
        insert_user_data_component_dict = {}

    def display_create_user(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        for x in self.all_component["create_user"]:
            self.all_component["create_user"][x].show()

    def display_insert_weather(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        for x in self.all_component['insert_weather']:
            self.all_component['insert_weather'][x].show()

    def display_change_user(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        userType_set = set(get_all_userType())

        count = self.all_component["change_user"]["myComboBox_userType"].count()
        for i in range(count):
            if self.all_component["change_user"]["myComboBox_userType"].itemText(i) in userType_set:
                userType_set.remove(self.all_component["change_user"]["myComboBox_userType"].itemText(i))
            else:
                self.all_component["change_user"]["myComboBox_userType"].remove(i)
        self.all_component["change_user"]["myComboBox_userType"].addItems(list(userType_set))

        for x in self.all_component['change_user']:
            self.all_component['change_user'][x].show()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def insert_user(self):
        userType = self.all_component['create_user']['myLineEdit_userType'].text()
        userName = self.all_component['create_user']['myLineEdit_userName'].text()
        gasUnit = self.all_component['create_user']['myLineEdit_gasUnit'].text()
        userUnit = self.all_component['create_user']['myLineEdit_userUnit'].text()
        remark = self.all_component['create_user']['myLineEdit_beizhu'].text()
        if userUnit and userName and gasUnit and userType:
            res = add_user(userType, userName, gasUnit, userUnit, remark)
            if res[0]:
                sec = QtGui.QMessageBox.information(self, "成功", "新建用户成功！", "确定")
                self.myLineEdit_userType.setText("")
                self.myLineEdit_userName.setText("")
                self.myLineEdit_gasUnit.setText("")
                self.myLineEdit_userUnit.setText("")
                self.myLineEdit_beizhu.setText("")
                print("success")
            else:
                warn = QtGui.QMessageBox.warning(self, "无法新建用户", res[1], "确定")
                print(res[1])
        else:
            warn = QtGui.QMessageBox.warning(self, "无法新建用户", "用户信息录入不全！", "确定")
            print("you can't")

    def insert_weather(self):
        date = self.all_component['insert_weather']['myDateEdit_date'].text()
        try:
            maxTemperature = float(self.all_component['insert_weather']['myLineEdit_maxTemperature'].text())
            minTemperature = float(self.all_component['insert_weather']['myLineEdit_minTemperature'].text())
            avgTemperature = float(self.all_component['insert_weather']['myLineEdit_avgTemperature'].text())
            if int(time.time()) < datetime_to_timestamp(date, '%Y/%m/%d'):
                QtGui.QMessageBox.warning(self, "天气录入失败", "不能录入未来日期的天气", "确定")
            elif date and maxTemperature and minTemperature and avgTemperature:
                add_weather(date, maxTemperature, minTemperature, avgTemperature)
                QtGui.QMessageBox.information(self, "天气录入成功", "天气录入成功", "确定")
            else:
                QtGui.QMessageBox.warning(self, "天气录入失败", "气温不能为空！", "确定")
        except IntegrityError:
            QtGui.QMessageBox.warning(self, "天气录入失败", "该日期的天气已被录入！", "确定")
        except ValueError:
            QtGui.QMessageBox.warning(self, "天气录入失败", "气温必须为数字！", "确定")
        except Exception as e:
            QtGui.QMessageBox.warning(self, "天气录入失败", "出现未知错误……", "确定")
            raise e
