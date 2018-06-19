import time
import datetime
from PyQt4 import QtGui, QtCore
from views.views_setting import view_setting
from control.user_operation import get_all_userType, get_userNames_by_userType, add_user, get_user_by_id, \
    update_user, delete_user
from control.data_operation import add_weather, datetime_to_timestamp, add_user_data, check_admin_password, \
    get_user_date_from_database, get_user_data_by_date_from_database, update_user_data_from_database, \
    delete_user_data_from_database
from control.user_operation import add_user, get_all_userType, get_userNames_by_userType
from control.data_operation import add_weather, datetime_to_timestamp, add_user_data
from control.user_operation import get_user_by_id, update_user, delete_user
from control.data_operation import export_gasIndex
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
        height = view_setting['ComboBoxHeight']
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
        height = view_setting['ComboBoxHeight']
        self.resize(width, height)
        self.setDate(QtCore.QDate.fromString(date, 'yyyy-MM-dd'))


class MyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        width = view_setting['DialogWidth']
        height = view_setting['DialogHeight']
        self.resize(width, height)


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
        self.comboBoxPair = {}
        self.userContent = {}
        self.nowUserId = 0

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

        delete_user = QtGui.QAction('删除用户', self)
        delete_user.setStatusTip('删除用户')
        self.delete_user_fuc()
        self.connect(delete_user, QtCore.SIGNAL('triggered()'), self.display_delete_user)
        user_menu.addAction(delete_user)

        insert_weather = QtGui.QAction('录入天气', self)
        insert_weather.setStatusTip('录入天气')
        self.insert_weather_fuc()
        self.connect(insert_weather, QtCore.SIGNAL('triggered()'), self.display_insert_weather)
        data_menu.addAction(insert_weather)

        insert_user_data = QtGui.QAction('录入用户数据', self)
        insert_user_data.setStatusTip('录入用户数据')
        self.insert_user_data_fuc()
        self.connect(insert_user_data, QtCore.SIGNAL('triggered()'), self.display_insert_user_data)
        data_menu.addAction(insert_user_data)

        maintain_data = QtGui.QAction('维护数据', self)
        maintain_data.setStatusTip('维护数据')
        self.maintain_data_fuc()
        self.connect(maintain_data, QtCore.SIGNAL('triggered()'), self.display_maintain_data)
        data_menu.addAction(maintain_data)

        dataExport_gasIndex = QtGui.QAction('导出用气指标', self)
        dataExport_gasIndex.setStatusTip('导出用气指标')
        self.dataExport_gasIndex_fuc()
        self.connect(dataExport_gasIndex, QtCore.SIGNAL('triggered()'), self.display_dataExport_gasIndex)
        data_menu.addAction(dataExport_gasIndex)

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
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        change_user_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myButton_insertUser = MyButton("修改", self)
        myButton_insertUser.move(100, 180)
        self.connect(myButton_insertUser, QtCore.SIGNAL("clicked()"), self.changeUserButtonSlot)
        change_user_component_dict["myButton_insertUser"] = myButton_insertUser

        self.all_component["change_user"] = change_user_component_dict
        for x in change_user_component_dict:
            change_user_component_dict[x].hide()

    def delete_user_fuc(self):
        delete_user_component_dict = {}
        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 60)
        delete_user_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        delete_user_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 120)
        delete_user_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 120)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        delete_user_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myButton_deleteUser = MyButton("删除", self)
        myButton_deleteUser.move(100, 180)

        cl = self

        def deleteUserButtonSlot():
            userId = cl.nowUserId
            warn = QtGui.QDialog()
            warn.resize(400, 150)
            warn.setWindowTitle("删除确认")
            warn.setWindowModality(QtCore.Qt.ApplicationModal)

            myLabel_info = MyLabel("确认将删除用户所有数据，确认删除吗？", warn)
            myLabel_info.resize(280, 30)
            myLabel_info.move(10, 10)
            myButton_yes = MyButton("确认", warn)
            myButton_yes.move(10, 100)
            myButton_no = MyButton("取消", warn)
            myButton_no.move(130, 100)

            def deleteUser():
                res = delete_user(userId)
                if res[0]:
                    QtGui.QMessageBox.information(warn, "成功", "删除用户成功！", "确定")
                    print("success")
                    warn.close()
                else:
                    QtGui.QMessageBox.warning(warn, "无法删除用户", res[1], "确定")
                    print(res[1])

            def cancel():
                warn.close()

            warn.connect(myButton_yes, QtCore.SIGNAL("clicked()"), deleteUser)
            warn.connect(myButton_no, QtCore.SIGNAL("clicked()"), cancel)

            warn.exec_()
            self.display_delete_user()

        self.connect(myButton_deleteUser, QtCore.SIGNAL("clicked()"), deleteUserButtonSlot)
        delete_user_component_dict["myButton_deleteUser"] = myButton_deleteUser

        self.all_component["delete_user"] = delete_user_component_dict
        for x in delete_user_component_dict:
            delete_user_component_dict[x].hide()

    def dataExport_gasIndex_fuc(self):
        dataExport_gasIndex_component_dict = {}
        myLabel_indexType = MyLabel("指标类型 : ", self)
        myLabel_indexType.move(100, 60)
        dataExport_gasIndex_component_dict["myLabel_indexType"] = myLabel_indexType

        myComboBox_indexType = MyComboBox(["年", "月"], self)
        myComboBox_indexType.move(200, 60)
        dataExport_gasIndex_component_dict["myComboBox_indexType"] = myComboBox_indexType

        myLabel_startTime = MyLabel("开始日期 : ", self)
        myLabel_startTime.move(100, 120)
        dataExport_gasIndex_component_dict["myLabel_startTime"] = myLabel_startTime

        myComboBox_startTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_startTime_year.move(200, 120)
        dataExport_gasIndex_component_dict["myComboBox_startTime_year"] = myComboBox_startTime_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 120)
        myLabel_year.resize(50, 30)
        dataExport_gasIndex_component_dict["myLabel_year"] = myLabel_year

        myComboBox_startTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_startTime_month.move(350, 120)
        dataExport_gasIndex_component_dict["myComboBox_startTime_month"] = myComboBox_startTime_month
        myLabel_month = MyLabel(" 月", self)
        myLabel_month.move(450, 120)
        myLabel_month.resize(50, 30)
        dataExport_gasIndex_component_dict["myLabel_month"] = myLabel_month

        myLabel_stopTime = MyLabel("结束日期 : ", self)
        myLabel_stopTime.move(100, 180)
        dataExport_gasIndex_component_dict["myLabel_stopTime"] = myLabel_stopTime

        myComboBox_stopTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_stopTime_year.move(200, 180)
        dataExport_gasIndex_component_dict["myComboBox_stopTime_year"] = myComboBox_stopTime_year
        myLabel_year2 = MyLabel(" 年", self)
        myLabel_year2.move(300, 180)
        myLabel_year2.resize(50, 30)
        dataExport_gasIndex_component_dict["myLabel_year2"] = myLabel_year2
        myComboBox_stopTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_stopTime_month.move(350, 180)
        dataExport_gasIndex_component_dict["myComboBox_stopTime_month"] = myComboBox_stopTime_month
        myLabel_month2 = MyLabel(" 月", self)
        myLabel_month2.move(450, 180)
        myLabel_month2.resize(50, 30)
        dataExport_gasIndex_component_dict["myLabel_month2"] = myLabel_month2

        myButton_export = MyButton("导出", self)
        myButton_export.move(100, 240)
        dataExport_gasIndex_component_dict["myButton_export"] = myButton_export

        self.all_component["dataExport_gasIndex"] = dataExport_gasIndex_component_dict

        pr = self

        def selectionChange():
            if pr.all_component["dataExport_gasIndex"]["myComboBox_indexType"].currentIndex() == 0:  # 指标类型是年
                pr.all_component["dataExport_gasIndex"]["myComboBox_startTime_month"].hide()
                pr.all_component["dataExport_gasIndex"]["myComboBox_stopTime_month"].hide()
                pr.all_component["dataExport_gasIndex"]["myLabel_month"].hide()
                pr.all_component["dataExport_gasIndex"]["myLabel_month2"].hide()
            elif pr.all_component["dataExport_gasIndex"]["myComboBox_indexType"].currentIndex() == 1:  # 指标类型是月
                pr.all_component["dataExport_gasIndex"]["myComboBox_startTime_month"].show()
                pr.all_component["dataExport_gasIndex"]["myComboBox_stopTime_month"].show()
                pr.all_component["dataExport_gasIndex"]["myLabel_month"].show()
                pr.all_component["dataExport_gasIndex"]["myLabel_month2"].show()

        self.all_component["dataExport_gasIndex"]["myComboBox_indexType"].currentIndexChanged.connect(selectionChange)

        for x in dataExport_gasIndex_component_dict:
            dataExport_gasIndex_component_dict[x].hide()

        def dataExportButtonSlot():
            timeType = myComboBox_indexType.currentText()
            if timeType == "年":
                start_time = myComboBox_startTime_year.currentText()
                stop_time = myComboBox_stopTime_year.currentText()
            elif timeType == "月":
                start_time = myComboBox_startTime_year.currentText() + "%2d" % (
                    int(myComboBox_startTime_month.currentText()))
                stop_time = myComboBox_stopTime_year.currentText() + "%2d" % (
                    int(myComboBox_stopTime_month.currentText()))
            else:
                raise RuntimeError("不存在的指标类型")

            now_time = "%4d%2d" % (datetime.datetime.now().year, datetime.datetime.now().month)
            if start_time > stop_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "开始时间不能大于结束时间", "确认")
            elif start_time > now_time or stop_time > now_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "不能选择未来的时间", "确认")
            else:
                file_path = QtGui.QFileDialog.getSaveFileName(self, 'save file', "用气指标",
                                                              "excel files (*.xls);;all files(*.*)")
                res = export_gasIndex(timeType, start_time, stop_time, file_path)
                if res[0]:
                    QtGui.QMessageBox.information(pr, "数据导出成功", "数据导出成功！", "确认")
                else:
                    QtGui.QMessageBox.warning(pr, "数据导出失败", res[1], "确认")

        self.connect(myButton_export, QtCore.SIGNAL("clicked()"), dataExportButtonSlot)


    def selectionchange(self):
        sender = self.sender()
        # print(sender)
        reciever = self.comboBoxPair[sender]
        # print("allcount:" + str(reciever.count()))

        while reciever.count() != 0:
            reciever.removeItem(0)
        # for i in range(reciever.count()):
        #     reciever.removeItem(i)
        # print("allcountnow:" + str(reciever.count()))

        now_userType = sender.itemText(sender.currentIndex())

        userNames, userName2id = get_userNames_by_userType(now_userType)
        self.userContent[now_userType] = userName2id

        reciever.addItems(userNames)

    def selectUser(self):
        sender = self.sender()
        last_sender = None
        for x in self.comboBoxPair:
            if self.comboBoxPair[x] == sender:
                last_sender = x
        if sender:
            now_userName = sender.itemText(sender.currentIndex())
        if last_sender:
            now_userType = last_sender.itemText(last_sender.currentIndex())
            if now_userType in self.userContent:
                self.nowUserId = self.userContent[now_userType][now_userName]
        # print(self.nowUserId)

    def changeUserButtonSlot(self):
        userId = self.nowUserId
        userContent = get_user_by_id(userId)
        d = MyDialog(self)

        myLabel_userType = MyLabel("用户类型 : ", d)
        myLabel_userType.move(100, 60)

        myLineEdit_userType = MyLineEdit(d)
        myLineEdit_userType.move(200, 60)
        myLineEdit_userType.setText(userContent["userType"])

        myLabel_userName = MyLabel("用户名称 : ", d)
        myLabel_userName.move(100, 120)

        myLineEdit_userName = MyLineEdit(d)
        myLineEdit_userName.move(200, 120)
        myLineEdit_userName.setText(userContent["userName"])

        myLabel_gasUnit = MyLabel("气量单位 : ", d)
        myLabel_gasUnit.move(100, 180)

        myLineEdit_gasUnit = MyLineEdit(d)
        myLineEdit_gasUnit.move(200, 180)
        myLineEdit_gasUnit.setText(userContent["gasUnit"])

        myLabel_userUnit = MyLabel("用户单位 : ", d)
        myLabel_userUnit.move(100, 240)

        myLineEdit_userUnit = MyLineEdit(d)
        myLineEdit_userUnit.move(200, 240)
        myLineEdit_userUnit.setText(userContent["userUnit"])

        myButton_insertUser = MyButton("确认", d)
        myButton_insertUser.move(100, 300)

        myButton_cancel = MyButton("取消", d)
        myButton_cancel.move(300, 300)

        def cancel():
            d.close()

        d.connect(myButton_cancel, QtCore.SIGNAL("clicked()"), cancel)

        def updateUser():
            userType = myLineEdit_userType.text()
            userName = myLineEdit_userName.text()
            gasUnit = myLineEdit_gasUnit.text()
            userUnit = myLineEdit_userUnit.text()
            if userUnit and userName and gasUnit and userType:
                res = update_user(userId, userType, userName, gasUnit, userUnit)
                if res[0]:
                    sec = QtGui.QMessageBox.information(d, "成功", "编辑用户成功！", "确定")
                    print("success")
                    d.close()
                else:
                    warn = QtGui.QMessageBox.warning(d, "无法编辑用户", res[1], "确定")
                    print(res[1])
            else:
                warn = QtGui.QMessageBox.warning(d, "无法编辑用户", "用户信息录入不全！", "确定")
                print("you can't")

        d.connect(myButton_insertUser, QtCore.SIGNAL("clicked()"), updateUser)

        d.setWindowTitle("编辑用户")
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        # print(d.parent().nowUserId)
        d.exec_()

        self.display_change_user()

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

        self.connect(myButton_insertWeather, QtCore.SIGNAL("clicked()"), self.insert_weather)

        self.all_component["insert_weather"] = insert_weather_component_dict
        for x in insert_weather_component_dict:
            insert_weather_component_dict[x].hide()

    def insert_user_data_fuc(self):
        insert_user_data_component_dict = {}

        myLabel_userType = MyLabel('用户类型：', self)
        myLabel_userType.move(100, 60)
        insert_user_data_component_dict['myLabel_userType'] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        insert_user_data_component_dict['myComboBox_userType'] = myComboBox_userType

        myLabel_userName = MyLabel('用户名称：', self)
        myLabel_userName.move(100, 120)
        insert_user_data_component_dict['myLabel_userName'] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 120)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        insert_user_data_component_dict['myComboBox_userName'] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myButton_logIn = MyButton('确认', self)
        myButton_logIn.move(100, 180)
        self.connect(myButton_logIn, QtCore.SIGNAL('clicked()'), self.insert_user_data_slot)
        insert_user_data_component_dict['myButton_logIn'] = myButton_logIn

        self.all_component['insert_user_data'] = insert_user_data_component_dict

        for i in insert_user_data_component_dict:
            insert_user_data_component_dict[i].hide()

    def insert_user_data_slot(self):
        userId = self.nowUserId
        userContent = get_user_by_id(userId)
        timeType = userContent['timeType']
        d = MyDialog(self)

        myLabel_title = MyLabel(userContent['userType'] + '-' + userContent['userName'] + '用户：', d)
        myLabel_title.move(100, 60)

        myLabel_gasCondition = MyLabel('用气工况：', d)
        myLabel_gasCondition.move(100, 120)

        def on_year_change():
            if myComboBox_year.currentText() == '':
                timeType > 1 and myComboBox_month.clear()
                timeType > 2 and myComboBox_day.clear()
                timeType > 3 and myComboBox_hour.clear()
            if timeType > 2:
                if myComboBox_month.currentText() == '2':
                    current_year = int(myComboBox_year.currentText())
                    while myComboBox_day.count() != 0:
                        myComboBox_day.removeItem(0)
                    if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                        myComboBox_day.addItems(day_dict['闰月'])
                    else:
                        myComboBox_day.addItems(day_dict['平月'])
                    if timeType != 5:
                        myComboBox_day.removeItem(0)

        myComboBox_year = MyComboBox([str(x) for x in range(2000, 2101)], d)
        myComboBox_year.move(200, 120)
        myComboBox_year.currentIndexChanged.connect(on_year_change)
        # myComboBox_year.addItems(list(range(2000, 2100)))

        myLabel_year = MyLabel('年', d)
        myLabel_year.move(300, 120)

        if timeType > 1:
            def on_month_change():
                if myComboBox_month.currentText() == '':
                    timeType > 2 and myComboBox_day.clear()
                    timeType > 3 and myComboBox_hour.clear()
                if timeType > 2:
                    myComboBox_day.clear()
                    current_month = myComboBox_month.currentText()
                    if current_month == '2':
                        current_year = int(myComboBox_year.currentText())
                        if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                            myComboBox_day.addItems(day_dict['闰月'])
                        else:
                            myComboBox_day.addItems(day_dict['平月'])
                    elif current_month in month_dict['大月']:
                        myComboBox_day.addItems(day_dict['大月'])
                    elif current_month in month_dict['小月']:
                        myComboBox_day.addItems(day_dict['小月'])
                    if timeType != 5:
                        myComboBox_day.removeItem(0)

            myComboBox_month = MyComboBox([''] + [str(x) for x in range(1, 13)], d)
            if timeType != 5:
                myComboBox_month.removeItem(0)
            # myComboBox_month.addItems(list(range(1, 13)))
            myComboBox_month.move(320, 120)
            myComboBox_month.currentIndexChanged.connect(on_month_change)

            myLabel_month = MyLabel('月', d)
            myLabel_month.move(420, 120)

            if timeType > 2:
                def on_day_change():
                    if timeType > 3:
                        if myComboBox_day.currentText() == '':
                            myComboBox_hour.clear()
                        else:
                            myComboBox_hour.addItems([''] + [str(x) for x in range(0, 24)])
                            if timeType != 5:
                                myComboBox_hour.removeItem(0)
                month_dict = {'大月': ['', '1', '3', '5', '7', '8', '10', '12'], '小月': ['', '4', '6', '9', '11']}
                day_dict = {'小月': [''] + [str(x) for x in range(1, 31)], '大月': [''] + [str(x) for x in range(1, 32)],
                            '平月': [''] + [str(x) for x in range(1, 29)], '闰月': [''] + [str(x) for x in range(1, 30)]}
                myComboBox_day = MyComboBox([str(x) for x in range(1, 32)], d)
                if timeType == 5:
                    myComboBox_day.clear()
                myComboBox_day.move(440, 120)
                myComboBox_day.currentIndexChanged.connect(on_day_change)

                myLabel_day = MyLabel('日', d)
                myLabel_day.move(540, 120)
                if timeType > 3:
                    myComboBox_hour = MyComboBox([str(x) for x in range(0, 24)], d)
                    if timeType == 5:
                        myComboBox_hour.clear()
                    myComboBox_hour.move(560, 120)

                    myLabel_hour = MyLabel('时', d)
                    myLabel_hour.move(660, 120)

        myLabel_gasNum = MyLabel('用气量：', d)
        myLabel_gasNum.move(100, 180)

        myLineEdit_gasNum = MyLineEdit(d)
        myLineEdit_gasNum.move(200, 180)

        myLabel_gasUnit = MyLabel(userContent['gasUnit'], d)
        myLabel_gasUnit.move(300, 180)

        myLabel_userNum = MyLabel('用户数：', d)
        myLabel_userNum.move(100, 240)

        myLineEdit_userNum = MyLineEdit(d)
        myLineEdit_userNum.move(200, 240)

        myLabel_userUnit = MyLabel(userContent['userUnit'], d)
        myLabel_userUnit.move(300, 240)

        myButton_insertUserData = MyButton("录入", d)
        myButton_insertUserData.move(100, 300)

        myButton_cancel = MyButton("取消", d)
        myButton_cancel.move(300, 300)

        def cancel():
            d.close()

        d.connect(myButton_cancel, QtCore.SIGNAL("clicked()"), cancel)

        def insert_user_data():
            gasNum = myLineEdit_gasNum.text()
            userNum = myLineEdit_userNum.text()
            year = int(myComboBox_year.currentText())
            month = day = hour = 0
            if timeType > 1:
                if myComboBox_month.currentText():
                    month = int(myComboBox_month.currentText())
            if timeType > 2:
                if myComboBox_day.currentText():
                    day = int(myComboBox_day.currentText())
            if timeType > 3:
                if myComboBox_hour.currentText():
                    hour = int(myComboBox_hour.currentText())
            if not gasNum:
                QtGui.QMessageBox.warning(d, "数据录入失败", "用气量不能为空！", "确定")
                return
            if not userNum:
                QtGui.QMessageBox.warning(d, "数据录入失败", "用户数不能为空！", "确定")
                return
            try:
                gasNum = float(gasNum)
                userNum = int(userNum)
                add_user_data(userId, timeType, gasNum, userNum, year, month, day, hour)
                QtGui.QMessageBox.information(d, "数据录入成功", "录入成功！", "确定")
            except ValueError:
                QtGui.QMessageBox.warning(d, "数据录入失败", "用气量和用户数必须为数字！", "确定")
            except IntegrityError:
                QtGui.QMessageBox.warning(d, '数据录入失败', '该日期的数据已被录入！', '确定')
            except Exception as e:
                QtGui.QMessageBox.warning(d, "数据录入失败", "出现未知错误……", "确定")
                raise e
        d.connect(myButton_insertUserData, QtCore.SIGNAL("clicked()"), insert_user_data)

        d.setWindowTitle("录入用户数据")
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        print(d.parent().nowUserId)
        d.exec_()

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

    def display_insert_user_data(self):
        for i in self.all_component.values():
            for j in i.values():
                j.hide()
        for i in self.all_component['insert_user_data'].values():
            i.show()

        userType_list = get_all_userType()

        self.all_component["insert_user_data"]["myComboBox_userType"].clear()
        self.all_component["insert_user_data"]["myComboBox_userType"].addItems(userType_list)

    def display_change_user(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        userType_list = get_all_userType()

        cb = self.all_component["change_user"]["myComboBox_userType"]
        while cb.count() != 0:
            cb.removeItem(0)
        cb.addItems(userType_list)

        for x in self.all_component['change_user']:
            self.all_component['change_user'][x].show()

    def display_delete_user(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        userType_list = get_all_userType()

        cb = self.all_component["delete_user"]["myComboBox_userType"]
        while cb.count() != 0:
            cb.removeItem(0)
        cb.addItems(userType_list)

        for x in self.all_component['delete_user']:
            self.all_component['delete_user'][x].show()

    def display_dataExport_gasIndex(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()

        for x in self.all_component['dataExport_gasIndex']:
            self.all_component['dataExport_gasIndex'][x].show()

        pr = self
        if pr.all_component["dataExport_gasIndex"]["myComboBox_indexType"].currentIndex() == 0:  # 指标类型是年
            pr.all_component["dataExport_gasIndex"]["myComboBox_startTime_month"].hide()
            pr.all_component["dataExport_gasIndex"]["myComboBox_stopTime_month"].hide()
            pr.all_component["dataExport_gasIndex"]["myLabel_month"].hide()
            pr.all_component["dataExport_gasIndex"]["myLabel_month2"].hide()
        elif pr.all_component["dataExport_gasIndex"]["myComboBox_indexType"].currentIndex() == 1:  # 指标类型是月
            pr.all_component["dataExport_gasIndex"]["myComboBox_startTime_month"].show()
            pr.all_component["dataExport_gasIndex"]["myComboBox_stopTime_month"].show()
            pr.all_component["dataExport_gasIndex"]["myLabel_month"].show()
            pr.all_component["dataExport_gasIndex"]["myLabel_month2"].show()


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
                self.all_component['create_user']['myLineEdit_userType'].setText("")
                self.all_component['create_user']['myLineEdit_userName'].setText("")
                self.all_component['create_user']['myLineEdit_gasUnit'].setText("")
                self.all_component['create_user']['myLineEdit_userUnit'].setText("")
                self.all_component['create_user']['myLineEdit_beizhu'].setText("")
                print("success")
            else:
                warn = QtGui.QMessageBox.warning(self, "无法新建用户", res[1], "确定")
                print(res[1])
        else:
            warn = QtGui.QMessageBox.warning(self, "无法新建用户", "用户信息录入不全！", "确定")
            print("you can't")

    def insert_weather(self):
        date = self.all_component['insert_weather']['myDateEdit_date'].text()
        maxTemperature = self.all_component['insert_weather']['myLineEdit_maxTemperature'].text()
        minTemperature = self.all_component['insert_weather']['myLineEdit_minTemperature'].text()
        avgTemperature = self.all_component['insert_weather']['myLineEdit_avgTemperature'].text()
        if not maxTemperature or not minTemperature or not avgTemperature:
            QtGui.QMessageBox.warning(self, "天气录入失败", "气温不能为空！", "确定")
            return
        try:
            maxTemperature = float(maxTemperature)
            minTemperature = float(minTemperature)
            avgTemperature = float(avgTemperature)
            if int(time.time()) < datetime_to_timestamp(date, '%Y/%m/%d'):
                QtGui.QMessageBox.warning(self, "天气录入失败", "不能录入未来日期的天气", "确定")
                return
            add_weather(date, maxTemperature, minTemperature, avgTemperature)
            QtGui.QMessageBox.information(self, "天气录入成功", "天气录入成功", "确定")
        except IntegrityError:
            QtGui.QMessageBox.warning(self, "天气录入失败", "该日期的天气已被录入！", "确定")
        except ValueError:
            QtGui.QMessageBox.warning(self, "天气录入失败", "气温必须为数字！", "确定")
        except Exception as e:
            QtGui.QMessageBox.warning(self, "天气录入失败", "出现未知错误……", "确定")
            raise e

    def maintain_data_fuc(self):
        maintain_data_compoment_dict = {}

        myLabel_adminName = MyLabel('管理者账号：', self)
        myLabel_adminName.move(100, 60)
        maintain_data_compoment_dict['myLabel_adminName'] = myLabel_adminName

        myLineEdit_adminName = MyLineEdit(self)
        myLineEdit_adminName.move(200, 60)
        maintain_data_compoment_dict['myLineEdit_adminName'] = myLineEdit_adminName

        myLabel_password = MyLabel('密码：', self)
        myLabel_password.move(100, 120)
        maintain_data_compoment_dict['myLabel_password'] = myLabel_password

        myLineEdit_password = MyLineEdit(self)
        myLineEdit_password.move(200, 120)
        myLineEdit_password.setEchoMode(QtGui.QLineEdit.Password)
        maintain_data_compoment_dict['myLineEdit_password'] = myLineEdit_password

        def maintain_data_login():
            username = myLineEdit_adminName.text()
            password = myLineEdit_password.text()
            if username and password:
                if check_admin_password(username, password):
                    self.maintain_data_search_slot()
                else:
                    QtGui.QMessageBox.warning(self, '登录失败', '密码错误', '确定')
            else:
                QtGui.QMessageBox.warning(self, '登录失败', '用户名和密码不能为空!', '确定')

        myButton_login = MyButton('登录', self)
        myButton_login.move(100, 180)
        self.connect(myButton_login, QtCore.SIGNAL('clicked()'), maintain_data_login)
        maintain_data_compoment_dict['myButton_login'] = myButton_login

        self.all_component['maintain_data'] = maintain_data_compoment_dict

        for i in maintain_data_compoment_dict.values():
            i.hide()

    def maintain_data_search_slot(self):
        d = MyDialog(self)
        self.date_dict = {}

        myLabel_userType = MyLabel('用户类型：', d)
        myLabel_userType.move(100, 60)

        myComboBox_userType = MyComboBox([], d)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)

        myLabel_userName = MyLabel('用户名称：', d)
        myLabel_userName.move(100, 120)

        myComboBox_userName = MyComboBox([], d)
        myComboBox_userName.move(200, 120)

        myLabel_date = MyLabel('日期：', d)
        myLabel_date.move(100, 180)

        def on_year_change():
            myComboBox_month.clear()
            if myComboBox_year.currentText() != '':
                myComboBox_month.addItems([str(x) for x in
                                           sorted(list(self.date_dict[int(myComboBox_year.currentText())].keys()))])

        myComboBox_year = MyComboBox([str(x) for x in range(2000, 2101)], d)
        myComboBox_year.move(200, 180)
        myComboBox_year.currentIndexChanged.connect(on_year_change)

        myLabel_year = MyLabel('年', d)
        myLabel_year.move(300, 180)

        def on_month_change():
            myComboBox_day.clear()
            if myComboBox_month.currentText() != '':
                myComboBox_day.addItems([str(x) for x in sorted(list(self.date_dict[int(myComboBox_year.currentText())]
                                                    [int(myComboBox_month.currentText())].keys()))])

        myComboBox_month = MyComboBox([str(x) for x in range(1, 13)], d)
        myComboBox_month.move(320, 180)
        myComboBox_month.currentIndexChanged.connect(on_month_change)

        myLabel_month = MyLabel('月', d)
        myLabel_month.move(420, 180)

        def on_day_change():
            myComboBox_hour.clear()
            if myComboBox_day.currentText() != '':
                myComboBox_hour.addItems([str(x) for x in sorted(list(self.date_dict[int(myComboBox_year.currentText())]
                                              [int(myComboBox_month.currentText())][int(myComboBox_day.currentText())]))])

        myComboBox_day = MyComboBox([str(x) for x in range(1, 32)], d)
        myComboBox_day.move(440, 180)
        myComboBox_day.currentIndexChanged.connect(on_day_change)

        myLabel_day = MyLabel('日', d)
        myLabel_day.move(540, 180)

        myComboBox_hour = MyComboBox([str(x) for x in range(0, 24)], d)
        myComboBox_hour.move(560, 180)

        myLabel_hour = MyLabel('时', d)
        myLabel_hour.move(660, 180)

        def on_userName_change():
            self.selectUser()
            update_date()

        def update_date():
            userContent = get_user_by_id(self.nowUserId)
            timeType = userContent['timeType']
            myLabel_year.hide()
            myComboBox_year.hide()
            myLabel_month.hide()
            myComboBox_month.hide()
            myLabel_day.hide()
            myComboBox_day.hide()
            myLabel_hour.hide()
            myComboBox_hour.hide()
            if timeType != 5:
                myLabel_year.show()
                myComboBox_year.show()
                if timeType > 1:
                    myLabel_month.show()
                    myComboBox_month.show()
                    if timeType > 2:
                        myLabel_day.show()
                        myComboBox_day.show()
                        if timeType > 3:
                            myLabel_hour.show()
                            myComboBox_hour.show()
            self.date_dict = get_user_date_from_database(self.nowUserId)
            myComboBox_year.clear()
            myComboBox_year.addItems([str(x) for x in sorted(list(self.date_dict.keys()))])

        def maintain_data_slot():
            try:
                d2 = MyDialog(d)
                year = int(myComboBox_year.currentText())
                month = int(myComboBox_month.currentText())
                day = int(myComboBox_day.currentText())
                hour = int(myComboBox_hour.currentText())
                user_data = get_user_data_by_date_from_database(self.nowUserId, year, month, day, hour)
            except ValueError:
                return
            user_data_id = user_data['id']
            user = get_user_by_id(self.nowUserId)
            timeType = user['timeType']

            myLabel_title = MyLabel(user['userType'] + '-' + user['userName'] + '用户：', d2)
            myLabel_title.move(100, 60)

            myLabel_gasCondition = MyLabel('用气工况：', d2)
            myLabel_gasCondition.move(100, 120)

            def on_newYear_change():
                if timeType > 2:
                    if myComboBox_newMonth.currentText() == '2':
                        current_year = int(myComboBox_newYear.currentText())
                        while myComboBox_newDay.count() != 0:
                            myComboBox_newDay.removeItem(0)
                        if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                            myComboBox_newDay.addItems(day_dict['闰月'])
                        else:
                            myComboBox_newDay.addItems(day_dict['平月'])

            myComboBox_newYear = MyComboBox([str(x) for x in range(2000, 2101)], d2)
            myComboBox_newYear.move(200, 120)
            myComboBox_newYear.currentIndexChanged.connect(on_newYear_change)
            myComboBox_newYear.setCurrentIndex(year - 2000)
            # myComboBox_year.addItems(list(range(2000, 2100)))

            myLabel_newYear = MyLabel('年', d2)
            myLabel_newYear.move(300, 120)

            if timeType > 1:
                def on_newMonth_change():
                    if timeType > 2:
                        myComboBox_newDay.clear()
                        current_month = myComboBox_newMonth.currentText()
                        if current_month == '2':
                            current_year = int(myComboBox_newYear.currentText())
                            if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                                myComboBox_newDay.addItems(day_dict['闰月'])
                            else:
                                myComboBox_newDay.addItems(day_dict['平月'])
                        elif current_month in month_dict['大月']:
                            myComboBox_newDay.addItems(day_dict['大月'])
                        elif current_month in month_dict['小月']:
                            myComboBox_newDay.addItems(day_dict['小月'])

                myComboBox_newMonth = MyComboBox([str(x) for x in range(1, 13)], d2)
                # myComboBox_newMonth.addItems(list(range(1, 13)))
                myComboBox_newMonth.move(320, 120)
                myComboBox_newMonth.currentIndexChanged.connect(on_newMonth_change)
                myComboBox_newMonth.setCurrentIndex(month - 1)

                myLabel_newMonth = MyLabel('月', d2)
                myLabel_newMonth.move(420, 120)

                if timeType > 2:
                    def on_newDay_change():
                        if timeType > 3:
                            if myComboBox_newDay.currentText() == '':
                                myComboBox_newHour.clear()
                            else:
                                myComboBox_newHour.addItems([str(x) for x in range(0, 24)])

                    month_dict = {'大月': ['1', '3', '5', '7', '8', '10', '12'], '小月': ['4', '6', '9', '11']}
                    day_dict = {'小月': [str(x) for x in range(1, 31)],
                                '大月': [str(x) for x in range(1, 32)],
                                '平月': [str(x) for x in range(1, 29)],
                                '闰月': [str(x) for x in range(1, 30)]}
                    myComboBox_newDay = MyComboBox([str(x) for x in range(1, 32)], d2)
                    myComboBox_newDay.move(440, 120)
                    myComboBox_newDay.currentIndexChanged.connect(on_newDay_change)
                    myComboBox_newDay.setCurrentIndex(day - 1)

                    myLabel_newDay = MyLabel('日', d2)
                    myLabel_newDay.move(540, 120)
                    if timeType > 3:
                        myComboBox_newHour = MyComboBox([str(x) for x in range(0, 24)], d2)
                        myComboBox_newHour.move(560, 120)
                        myComboBox_newHour.setCurrentIndex(hour)

                        myLabel_newHour = MyLabel('时', d2)
                        myLabel_newHour.move(660, 120)

            myLabel_gasNum = MyLabel('用气量：', d2)
            myLabel_gasNum.move(100, 180)

            myLineEdit_gasNum = MyLineEdit(d2)
            myLineEdit_gasNum.move(200, 180)
            myLineEdit_gasNum.setText(str(user_data['gasNum']))

            myLabel_gasUnit = MyLabel(user['gasUnit'], d2)
            myLabel_gasUnit.move(300, 180)

            myLabel_userNum = MyLabel('用户数：', d2)
            myLabel_userNum.move(100, 240)

            myLineEdit_userNum = MyLineEdit(d2)
            myLineEdit_userNum.move(200, 240)
            myLineEdit_userNum.setText(str(user_data['userNum']))

            myLabel_userUnit = MyLabel(user['userUnit'], d2)
            myLabel_userUnit.move(300, 240)

            myButton_insertUserData = MyButton("修改", d2)
            myButton_insertUserData.move(100, 300)

            myButton_cancel = MyButton("删除", d2)
            myButton_cancel.move(300, 300)

            def delete_user_data():
                if not QtGui.QMessageBox.question(d2, '确认删除', '确认删除吗？', '确认', '取消'):
                    delete_user_data_from_database(user_data_id)
                    d2.close()
                    update_date()

            d2.connect(myButton_cancel, QtCore.SIGNAL("clicked()"), delete_user_data)

            def update_user_data():
                gasNum = myLineEdit_gasNum.text()
                userNum = myLineEdit_userNum.text()
                newYear = int(myComboBox_newYear.currentText())
                newMonth = newDay = newHour = 0
                if timeType > 1:
                    if myComboBox_newMonth.currentText():
                        newMonth = int(myComboBox_newMonth.currentText())
                if timeType > 2:
                    if myComboBox_newDay.currentText():
                        newDay = int(myComboBox_newDay.currentText())
                if timeType > 3:
                    if myComboBox_newHour.currentText():
                        newHour = int(myComboBox_newHour.currentText())
                if not gasNum:
                    QtGui.QMessageBox.warning(d2, "数据修改失败", "用气量不能为空！", "确定")
                    return
                if not userNum:
                    QtGui.QMessageBox.warning(d2, "数据修改失败", "用户数不能为空！", "确定")
                    return
                try:
                    gasNum = float(gasNum)
                    userNum = int(userNum)
                    update_user_data_from_database(user_data_id, gasNum, userNum, newYear, newMonth, newDay, newHour)
                    QtGui.QMessageBox.information(d2, "数据修改成功", "修改成功！", "确定")
                    d2.close()
                    update_date()
                except ValueError:
                    QtGui.QMessageBox.warning(d2, "数据修改失败", "用气量和用户数必须为数字！", "确定")
                except IntegrityError:
                    QtGui.QMessageBox.warning(d2, '数据修改失败', '该日期的数据已被录入！', '确定')
                except Exception as e:
                    QtGui.QMessageBox.warning(d2, "数据修改失败", "出现未知错误……", "确定")
                    raise e

            d2.connect(myButton_insertUserData, QtCore.SIGNAL("clicked()"), update_user_data)

            d2.setWindowTitle("修改用户数据")
            d2.setWindowModality(QtCore.Qt.ApplicationModal)
            d2.exec_()

        myButton_search = MyButton('查询', d)
        myButton_search.move(100, 240)
        d.connect(myButton_search, QtCore.SIGNAL('clicked()'), maintain_data_slot)

        myComboBox_userName.currentIndexChanged.connect(on_userName_change)
        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        def update_userType():
            userType_list = get_all_userType()
            myComboBox_userType.clear()
            myComboBox_userType.addItems(userType_list)
        update_userType()

        d.setWindowTitle("查询用户数据")
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()

    def display_maintain_data(self):
        for i in self.all_component.values():
            for j in i.values():
                j.hide()
        for i in self.all_component['maintain_data'].values():
            i.show()
