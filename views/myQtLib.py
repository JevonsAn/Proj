import time
import datetime

from copy import deepcopy
from pymysql import IntegrityError

import pyqtgraph as pg
# from PyQt4 import QtGui, QtCore
from pyqtgraph import QtGui, QtCore
from views.views_setting import view_setting

from control.user_operation import add_user, get_all_userType, get_userNames_by_userType
from control.user_operation import get_user_by_id, update_user, delete_user

from control.data_operation import check_admin_password, get_user_data_by_date_from_database
from control.data_operation import update_user_data_from_database, delete_user_data_from_database
from control.data_operation import add_weather, datetime_to_timestamp, add_user_data
from control.data_operation import export_gasIndex, export_uneven

from control.gas_index_opeartion import get_gas_index_from_database, get_index_of_user_in_times_from_database
from control.gas_index_opeartion import get_weather_in_times_from_database

from control.uneven_operation import search_uneven, get_uneven_list

from control.predict_operation import human_predict_userNum, model_predict_userNum, model_predict_gasIndex

month_dict = {'大月': ['', '1', '3', '5', '7', '8', '10', '12'], '小月': ['', '4', '6', '9', '11']}
day_dict = {'小月': [''] + [str(x) for x in range(1, 31)], '大月': [''] + [str(x) for x in range(1, 32)],
            '平月': [''] + [str(x) for x in range(1, 29)], '闰月': [''] + [str(x) for x in range(1, 30)]}


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


class MyTable(QtGui.QTableWidget):
    def __init__(self, parent, table, header):
        QtGui.QTableWidget.__init__(self, parent)
        rows_num = len(table)
        columns_num = len(header)
        self.setRowCount(rows_num)
        self.setColumnCount(columns_num)
        self.setHorizontalHeaderLabels(header)
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.resize(view_setting['TableWidth'], view_setting['TableHeight'])
        for i in range(rows_num):
            for j in range(columns_num):
                self.setItem(i, j, QtGui.QTableWidgetItem(str(table[i][j])))
                self.item(i, j).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)


class MyPainter(QtGui.QPainter):
    def __init__(self, parent, leftBottom = (0, 0)):
        super(MyPainter, self).__init__(parent)
        self.leftBottom = leftBottom

    def setLeftBottom(self, x, y):
        self.leftBottom = (x, y)

    def drawLine(self, *__args):
        super().drawLine(self.leftBottom[0] + __args[0], self.leftBottom[1] - __args[1],
                   self.leftBottom[0] + __args[2], self.leftBottom[1] - __args[3])

    def drawText(self, *__args):
        super().drawText(self.leftBottom[0] + __args[0], self.leftBottom[1] - __args[1], __args[2])


class MyPlot(pg.PlotWidget):
    def __init__(self, parent, index_data, index_unit, weather_data, title=''):
        x_dict = {x: index_data[x][0] for x in range(len(index_data))}
        axis = [(x, index_data[x][0]) for x in range(0, len(index_data), 5)]
        string_x_unit = pg.AxisItem(orientation='bottom')
        string_x_unit.setTicks([axis, x_dict.items()])
        vb = pg.ViewBox()
        pg.PlotWidget.__init__(self, parent, axisItems={'bottom': string_x_unit}, title=title, viewBox=vb)
        self.resize(view_setting['PlotWidth'], view_setting['PlotHeight'])
        p = self.plot()
        label = pg.TextItem()
        self.addItem(label)
        self.addLegend(size=(80, 80))
        self.showGrid(x=True, y=True, alpha=0.5)
        self.plot(x=list(x_dict.keys()), y=[row[1] for row in index_data], pen='r', name='指标', symbolBrush=(255, 0, 0))
        # if weather_data:
        #     weather_plot = self.plot(x=list(x_dict.keys()), y=[row[3] for row in weather_data], pen='b', name='气温', symbolBrush=(0, 0, 255))
        self.setLabel(axis='left', text='指标')
        self.setLabel(axis='bottom', text='日期')
        self.setBackground(None)
        vLine = pg.InfiniteLine(angle=90, movable=False, )
        hLine = pg.InfiniteLine(angle=0, movable=False, )
        self.addItem(vLine, ignoreBounds=True)
        self.addItem(hLine, ignoreBounds=True)

        def mouseMoved(evt):
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if self.sceneBoundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)
                index = int(mousePoint.x())
                pos_y = int(mousePoint.y())
                # print(index)
                if 0 <= index < len(index_data):
                    # if weather_data:
                    #     label.setHtml(
                    #         "<p style='color:black'>日期：{0}</p>"
                    #         "<p style='color:black'>指标：{1}{2}</p>"
                    #         "<p style='color:black'>气温：{3}℃</p>".format(
                    #             x_dict[index], index_data[index][1], index_unit, weather_data[index][3]))
                    # else:
                    label.setHtml(
                        "<p style='color:black'>日期：{0}</p>"
                        "<p style='color:black'>指标：{1}{2}</p>".format(
                            x_dict[index], index_data[index][1], index_unit))
                    label.setPos(mousePoint.x(), mousePoint.y())
                vLine.setPos(mousePoint.x())
                hLine.setPos(mousePoint.y())
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=30, slot=mouseMoved)


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

        dataExport_uneven = QtGui.QAction('导出不均匀系数', self)
        dataExport_uneven.setStatusTip('导出不均匀系数')
        self.dataExport_uneven_fuc()
        self.connect(dataExport_uneven, QtCore.SIGNAL('triggered()'), self.display_dataExport_uneven)
        data_menu.addAction(dataExport_uneven)

        search_gas_index = QtGui.QAction('用气指标查询', self)
        search_gas_index.setStatusTip('用气指标查询')
        self.search_gas_index_fuc()
        self.connect(search_gas_index, QtCore.SIGNAL('triggered()'), self.display_search_gas_index)
        yongqi_menu.addAction(search_gas_index)

        examine_index_result = QtGui.QAction('结果查看', self)
        examine_index_result.setStatusTip('用气指标结果查看')
        self.examine_index_result_fuc()
        self.connect(examine_index_result, QtCore.SIGNAL('triggered()'), self.display_examine_index_result)
        yongqi_menu.addAction(examine_index_result)

        human_predict = QtGui.QAction('发展规模干预预测', self)
        human_predict.setStatusTip('发展规模干预预测')
        self.human_predict_fuc()
        self.connect(human_predict, QtCore.SIGNAL('triggered()'), self.display_human_predict)
        yongqi_menu.addAction(human_predict)

        model_predict = QtGui.QAction('发展规模模型预测', self)
        model_predict.setStatusTip('发展规模模型预测')
        self.model_predict_fuc()
        self.connect(model_predict, QtCore.SIGNAL('triggered()'), self.display_model_predict)
        yongqi_menu.addAction(model_predict)

        index_predict = QtGui.QAction('用气指标预测', self)
        index_predict.setStatusTip('用气指标预测')
        self.index_predict_fuc()
        self.connect(index_predict, QtCore.SIGNAL('triggered()'), self.display_index_predict)
        yongqi_menu.addAction(index_predict)

        uneven_search = QtGui.QAction('不均匀系数查询', self)
        uneven_search.setStatusTip('不均匀系数查询')
        self.uneven_search_fuc()
        self.connect(uneven_search, QtCore.SIGNAL('triggered()'), self.display_uneven_search)
        xishu_menu.addAction(uneven_search)

        uneven_watch = QtGui.QAction('结果查看', self)
        uneven_watch.setStatusTip('不均匀系数结果查看')
        self.uneven_watch_fuc()
        self.connect(uneven_watch, QtCore.SIGNAL('triggered()'), self.display_uneven_watch)
        xishu_menu.addAction(uneven_watch)

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
                # 正在导出的提示
                res = export_gasIndex(timeType, start_time, stop_time, file_path)
                if res[0]:
                    QtGui.QMessageBox.information(pr, "数据导出成功", "数据导出成功！", "确认")
                else:
                    QtGui.QMessageBox.warning(pr, "数据导出失败", res[1], "确认")

        self.connect(myButton_export, QtCore.SIGNAL("clicked()"), dataExportButtonSlot)

    def dataExport_uneven_fuc(self):
        dataExport_uneven_component_dict = {}
        myLabel_indexType = MyLabel("系数类型 : ", self)
        myLabel_indexType.move(100, 60)
        dataExport_uneven_component_dict["myLabel_indexType"] = myLabel_indexType

        myComboBox_indexType = MyComboBox(["月", "周", "日", "小时"], self)
        myComboBox_indexType.move(200, 60)
        dataExport_uneven_component_dict["myComboBox_indexType"] = myComboBox_indexType

        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 120)
        dataExport_uneven_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 120)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        dataExport_uneven_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 180)
        dataExport_uneven_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 180)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        dataExport_uneven_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myLabel_startTime = MyLabel("开始日期 : ", self)
        myLabel_startTime.move(100, 240)
        dataExport_uneven_component_dict["myLabel_startTime"] = myLabel_startTime

        myComboBox_startTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_startTime_year.move(200, 240)
        dataExport_uneven_component_dict["myComboBox_startTime_year"] = myComboBox_startTime_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 240)
        myLabel_year.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_year"] = myLabel_year

        myComboBox_startTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_startTime_month.move(350, 240)
        dataExport_uneven_component_dict["myComboBox_startTime_month"] = myComboBox_startTime_month
        myLabel_month = MyLabel(" 月", self)
        myLabel_month.move(450, 240)
        myLabel_month.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_month"] = myLabel_month

        myComboBox_startTime_day = MyComboBox([str(s) for s in range(1, 31)], self)
        myComboBox_startTime_day.move(500, 240)
        dataExport_uneven_component_dict["myComboBox_startTime_day"] = myComboBox_startTime_day
        myLabel_day = MyLabel(" 日", self)
        myLabel_day.move(600, 240)
        myLabel_day.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_day"] = myLabel_day

        myComboBox_startTime_week = MyComboBox([], self)
        myComboBox_startTime_week.move(500, 240)
        dataExport_uneven_component_dict["myComboBox_startTime_week"] = myComboBox_startTime_week
        myLabel_week = MyLabel(" 周", self)
        myLabel_week.move(600, 240)
        myLabel_week.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_week"] = myLabel_week

        myComboBox_startTime_hour = MyComboBox([str(s) for s in range(1, 25)], self)
        myComboBox_startTime_hour.move(650, 240)
        dataExport_uneven_component_dict["myComboBox_startTime_hour"] = myComboBox_startTime_hour
        myLabel_hour = MyLabel(" 小时", self)
        myLabel_hour.move(750, 240)
        myLabel_hour.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_hour"] = myLabel_hour

        myLabel_stopTime = MyLabel("结束日期 : ", self)
        myLabel_stopTime.move(100, 300)
        dataExport_uneven_component_dict["myLabel_stopTime"] = myLabel_stopTime

        myComboBox_stopTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_stopTime_year.move(200, 300)
        dataExport_uneven_component_dict["myComboBox_stopTime_year"] = myComboBox_stopTime_year
        myLabel_year2 = MyLabel(" 年", self)
        myLabel_year2.move(300, 300)
        myLabel_year2.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_year2"] = myLabel_year2

        myComboBox_stopTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_stopTime_month.move(350, 300)
        dataExport_uneven_component_dict["myComboBox_stopTime_month"] = myComboBox_stopTime_month
        myLabel_month2 = MyLabel(" 月", self)
        myLabel_month2.move(450, 300)
        myLabel_month2.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_month2"] = myLabel_month2

        myComboBox_stopTime_day = MyComboBox([str(s) for s in range(1, 31)], self)
        myComboBox_stopTime_day.move(500, 300)
        dataExport_uneven_component_dict["myComboBox_stopTime_day"] = myComboBox_stopTime_day
        myLabel_day2 = MyLabel(" 日", self)
        myLabel_day2.move(600, 300)
        myLabel_day2.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_day2"] = myLabel_day2

        myComboBox_stopTime_week = MyComboBox([], self)
        myComboBox_stopTime_week.move(500, 300)
        dataExport_uneven_component_dict["myComboBox_stopTime_week"] = myComboBox_stopTime_week
        myLabel_week2 = MyLabel(" 周", self)
        myLabel_week2.move(600, 300)
        myLabel_week2.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_week2"] = myLabel_week2

        myComboBox_stopTime_hour = MyComboBox([str(s) for s in range(1, 25)], self)
        myComboBox_stopTime_hour.move(650, 300)
        dataExport_uneven_component_dict["myComboBox_stopTime_hour"] = myComboBox_stopTime_hour
        myLabel_hour2 = MyLabel(" 小时", self)
        myLabel_hour2.move(750, 300)
        myLabel_hour2.resize(50, 30)
        dataExport_uneven_component_dict["myLabel_hour2"] = myLabel_hour2

        myButton_export = MyButton("导出", self)
        myButton_export.move(100, 360)
        dataExport_uneven_component_dict["myButton_export"] = myButton_export

        month_dict = {'大月': ['1', '3', '5', '7', '8', '10', '12'], '小月': ['4', '6', '9', '11']}
        day_dict = {'小月': [str(x) for x in range(1, 31)], '大月': [str(x) for x in range(1, 32)],
                    '平月': [str(x) for x in range(1, 29)], '闰月': [str(x) for x in range(1, 30)]}

        def on_year_change():
            sender = self.sender()
            if sender.count() == 0:
                return

            if sender == myComboBox_startTime_year:
                month = myComboBox_startTime_month
                day = myComboBox_startTime_day
                week = myComboBox_startTime_week
            elif sender == myComboBox_stopTime_year:
                month = myComboBox_stopTime_month
                day = myComboBox_stopTime_day
                week = myComboBox_stopTime_week
            else:
                return

            current_month = int(month.currentText())
            current_year = int(sender.currentText())

            if str(current_month) == '2':
                day.clear()
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    day.addItems(day_dict['闰月'])
                else:
                    day.addItems(day_dict['平月'])
            day_list_len = day.count()
            week.clear()
            mondays = []
            for y, m, d in [(current_year, current_month, int(x)) for x in range(1, day_list_len + 1)]:
                if datetime.datetime(y, m, d).strftime("%w") == '1':
                    mondays.append(d)
            weeks_list = []
            for d in mondays:
                sr = d
                sp = (d + 6) % (day_list_len)
                if sp == 0:
                    sp = day_list_len
                weeks_list.append("%d日~%d日" % (sr, sp))
            week.addItems(weeks_list)


        def on_month_change():
            sender = self.sender()
            if sender.count() == 0:
                return

            if sender == myComboBox_startTime_month:
                year = myComboBox_startTime_year
                day = myComboBox_startTime_day
                week = myComboBox_startTime_week
            elif sender == myComboBox_stopTime_month:
                year = myComboBox_stopTime_year
                day = myComboBox_stopTime_day
                week = myComboBox_stopTime_week
            else:
                return

            current_month = int(sender.currentText())
            current_year = int(year.currentText())

            day.clear()
            day_list = []
            if current_month == 2:
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    day_list = day_dict['闰月']
                else:
                    day_list = day_dict['平月']
            elif str(current_month) in month_dict['大月']:
                day_list = day_dict['大月']
            elif str(current_month) in month_dict['小月']:
                day_list = day_dict['小月']
            day.addItems(day_list)

            week.clear()
            mondays = []
            for y, m, d in [(current_year, current_month, int(x)) for x in day_list]:
                if datetime.datetime(y, m, d).strftime("%w") == '1':
                    mondays.append(d)
            weeks_list = []
            for d in mondays:
                sr = d
                sp = (d + 6) % (len(day_list))
                if sp == 0:
                    sp = len(day_list)
                weeks_list.append("%d日~%d日" % (sr, sp))
            week.addItems(weeks_list)

        pr = self
        month_component_list = [myComboBox_startTime_month, myComboBox_stopTime_month, myLabel_month, myLabel_month2]
        day_component_list = [myComboBox_startTime_day, myComboBox_stopTime_day, myLabel_day, myLabel_day2]
        week_component_list = [myComboBox_startTime_week, myComboBox_stopTime_week, myLabel_week, myLabel_week2]
        hour_component_list = [myComboBox_startTime_hour, myComboBox_stopTime_hour, myLabel_hour, myLabel_hour2]

        def selectionChange():
            if myComboBox_indexType.currentIndex() == 0:  # 指标类型是月
                # for x in month_component_list + day_component_list + hour_component_list:
                #     x.hide()
                for x in day_component_list + hour_component_list + week_component_list:
                    x.hide()
                for x in month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 1:  # 指标类型是周
                for x in hour_component_list + day_component_list:
                    x.hide()
                for x in week_component_list + month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 2:  # 指标类型是日
                for x in hour_component_list + week_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 3:  # 指标类型是小时
                for x in week_component_list:
                    x.hide()
                for x in month_component_list + day_component_list + hour_component_list:
                    x.show()

        myComboBox_startTime_year.currentIndexChanged.connect(on_year_change)
        myComboBox_startTime_month.currentIndexChanged.connect(on_month_change)
        myComboBox_stopTime_year.currentIndexChanged.connect(on_year_change)
        myComboBox_stopTime_month.currentIndexChanged.connect(on_month_change)
        myComboBox_indexType.currentIndexChanged.connect(selectionChange)
        self.all_component["dataExport_uneven"] = dataExport_uneven_component_dict

        for x in dataExport_uneven_component_dict:
            dataExport_uneven_component_dict[x].hide()

        pr = self

        def dataExportButtonSlot():
            timeType = myComboBox_indexType.currentText()

            def getTime(timeType):
                if timeType == "月":
                    start_time = myComboBox_startTime_year.currentText() + "%2d" % (
                        int(myComboBox_startTime_month.currentText()))
                    stop_time = myComboBox_stopTime_year.currentText() + "%2d" % (
                        int(myComboBox_stopTime_month.currentText()))
                    now_time = "%4d%2d" % (datetime.datetime.now().year, datetime.datetime.now().month)
                elif timeType == "日":
                    start_time = "%s%2d%2d" % (
                    myComboBox_startTime_year.currentText(), int(myComboBox_startTime_month.currentText()),
                    int(myComboBox_startTime_day.currentText()))
                    stop_time = "%s%2d%2d" % (
                    myComboBox_stopTime_year.currentText(), int(myComboBox_stopTime_month.currentText()),
                    int(myComboBox_stopTime_day.currentText()))
                    now_time = "%4d%2d%2d" % (
                    datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                elif timeType == "周":
                    text1 = myComboBox_startTime_week.currentText()
                    text2 = myComboBox_stopTime_week.currentText()
                    start_day = int(text1.strip().split("日~")[0])
                    stop_day0 = int(text2.strip().split("日~")[0])
                    stop_day = int(text2.strip().split("日~")[-1][:-1])
                    stop_month = int(myComboBox_stopTime_month.currentText())
                    stop_year = int(myComboBox_stopTime_year.currentText())
                    if stop_day >= stop_day0:
                        stop_month += 1
                        if stop_month > 12:
                            stop_month = stop_month % 12
                            stop_year += 1

                    start_time = "%s%2d%2d" % (
                        myComboBox_startTime_year.currentText(), int(myComboBox_startTime_month.currentText()),
                        int(start_day))
                    stop_time = "%4d%2d%2d" % (stop_year, stop_month, stop_day)
                    now_time = "%4d%2d%2d" % (
                    datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                elif timeType == "小时":
                    start_time = "%s%2d%2d%2d" % (
                    myComboBox_startTime_year.currentText(), int(myComboBox_startTime_month.currentText()),
                    int(myComboBox_startTime_day.currentText()), int(myComboBox_startTime_hour.currentText()))
                    stop_time = "%s%2d%2d%2d" % (
                    myComboBox_stopTime_year.currentText(), int(myComboBox_stopTime_month.currentText()),
                    int(myComboBox_stopTime_day.currentText()), int(myComboBox_stopTime_hour.currentText()))
                    now_time = "%4d%2d%2d%2d" % (
                    datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day,
                    datetime.datetime.now().hour)
                else:
                    raise RuntimeError("不存在的指标类型")

                return start_time, stop_time, now_time

            start_time, stop_time, now_time = getTime(timeType)
            # print(start_time, stop_time, now_time)
            if start_time > stop_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "开始时间不能大于结束时间", "确认")
            elif start_time > now_time or stop_time > now_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "不能选择未来的时间", "确认")
            else:
                user = get_user_by_id(pr.nowUserId)
                file_path = QtGui.QFileDialog.getSaveFileName(pr, 'save file', "%s-%s用户%s不均匀系数" % (
                user["userType"], user["userName"], timeType),
                                                              "excel files (*.xls);;all files(*.*)")
                res = export_uneven(pr.nowUserId, timeType, start_time, stop_time, file_path)
                if res[0]:
                    QtGui.QMessageBox.information(pr, "数据导出成功", "数据导出成功！", "确认")
                else:
                    QtGui.QMessageBox.warning(pr, "数据导出失败", res[1], "确认")

        self.connect(myButton_export, QtCore.SIGNAL("clicked()"), dataExportButtonSlot)

    def uneven_watch_fuc(self):
        uneven_watch_component_dict = {}
        myLabel_indexType = MyLabel("系数类型 : ", self)
        myLabel_indexType.move(100, 60)
        uneven_watch_component_dict["myLabel_indexType"] = myLabel_indexType

        myComboBox_indexType = MyComboBox(["月", "周", "日", "小时"], self)
        myComboBox_indexType.move(200, 60)
        uneven_watch_component_dict["myComboBox_indexType"] = myComboBox_indexType

        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 120)
        uneven_watch_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 120)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        uneven_watch_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 180)
        uneven_watch_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 180)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        uneven_watch_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myLabel_startTime = MyLabel("开始日期 : ", self)
        myLabel_startTime.move(100, 240)
        uneven_watch_component_dict["myLabel_startTime"] = myLabel_startTime

        myComboBox_startTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_startTime_year.move(200, 240)
        uneven_watch_component_dict["myComboBox_startTime_year"] = myComboBox_startTime_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 240)
        myLabel_year.resize(50, 30)
        uneven_watch_component_dict["myLabel_year"] = myLabel_year

        myComboBox_startTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_startTime_month.move(350, 240)
        uneven_watch_component_dict["myComboBox_startTime_month"] = myComboBox_startTime_month
        myLabel_month = MyLabel(" 月", self)
        myLabel_month.move(450, 240)
        myLabel_month.resize(50, 30)
        uneven_watch_component_dict["myLabel_month"] = myLabel_month

        myComboBox_startTime_day = MyComboBox([str(s) for s in range(1, 31)], self)
        myComboBox_startTime_day.move(500, 240)
        uneven_watch_component_dict["myComboBox_startTime_day"] = myComboBox_startTime_day
        myLabel_day = MyLabel(" 日", self)
        myLabel_day.move(600, 240)
        myLabel_day.resize(50, 30)
        uneven_watch_component_dict["myLabel_day"] = myLabel_day

        myComboBox_startTime_week = MyComboBox([], self)
        myComboBox_startTime_week.move(500, 240)
        uneven_watch_component_dict["myComboBox_startTime_week"] = myComboBox_startTime_week
        myLabel_week = MyLabel(" 周", self)
        myLabel_week.move(600, 240)
        myLabel_week.resize(50, 30)
        uneven_watch_component_dict["myLabel_week"] = myLabel_week

        myComboBox_startTime_hour = MyComboBox([str(s) for s in range(1, 25)], self)
        myComboBox_startTime_hour.move(650, 240)
        uneven_watch_component_dict["myComboBox_startTime_hour"] = myComboBox_startTime_hour
        myLabel_hour = MyLabel(" 小时", self)
        myLabel_hour.move(750, 240)
        myLabel_hour.resize(50, 30)
        uneven_watch_component_dict["myLabel_hour"] = myLabel_hour

        myLabel_stopTime = MyLabel("结束日期 : ", self)
        myLabel_stopTime.move(100, 300)
        uneven_watch_component_dict["myLabel_stopTime"] = myLabel_stopTime

        myComboBox_stopTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_stopTime_year.move(200, 300)
        uneven_watch_component_dict["myComboBox_stopTime_year"] = myComboBox_stopTime_year
        myLabel_year2 = MyLabel(" 年", self)
        myLabel_year2.move(300, 300)
        myLabel_year2.resize(50, 30)
        uneven_watch_component_dict["myLabel_year2"] = myLabel_year2

        myComboBox_stopTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_stopTime_month.move(350, 300)
        uneven_watch_component_dict["myComboBox_stopTime_month"] = myComboBox_stopTime_month
        myLabel_month2 = MyLabel(" 月", self)
        myLabel_month2.move(450, 300)
        myLabel_month2.resize(50, 30)
        uneven_watch_component_dict["myLabel_month2"] = myLabel_month2

        myComboBox_stopTime_day = MyComboBox([str(s) for s in range(1, 31)], self)
        myComboBox_stopTime_day.move(500, 300)
        uneven_watch_component_dict["myComboBox_stopTime_day"] = myComboBox_stopTime_day
        myLabel_day2 = MyLabel(" 日", self)
        myLabel_day2.move(600, 300)
        myLabel_day2.resize(50, 30)
        uneven_watch_component_dict["myLabel_day2"] = myLabel_day2

        myComboBox_stopTime_week = MyComboBox([], self)
        myComboBox_stopTime_week.move(500, 300)
        uneven_watch_component_dict["myComboBox_stopTime_week"] = myComboBox_stopTime_week
        myLabel_week2 = MyLabel(" 周", self)
        myLabel_week2.move(600, 300)
        myLabel_week2.resize(50, 30)
        uneven_watch_component_dict["myLabel_week2"] = myLabel_week2

        myComboBox_stopTime_hour = MyComboBox([str(s) for s in range(1, 25)], self)
        myComboBox_stopTime_hour.move(650, 300)
        uneven_watch_component_dict["myComboBox_stopTime_hour"] = myComboBox_stopTime_hour
        myLabel_hour2 = MyLabel(" 小时", self)
        myLabel_hour2.move(750, 300)
        myLabel_hour2.resize(50, 30)
        uneven_watch_component_dict["myLabel_hour2"] = myLabel_hour2

        myButton_export = MyButton("查看", self)
        myButton_export.move(100, 360)
        uneven_watch_component_dict["myButton_export"] = myButton_export

        month_dict = {'大月': ['1', '3', '5', '7', '8', '10', '12'], '小月': ['4', '6', '9', '11']}
        day_dict = {'小月': [str(x) for x in range(1, 31)], '大月': [str(x) for x in range(1, 32)],
                    '平月': [str(x) for x in range(1, 29)], '闰月': [str(x) for x in range(1, 30)]}

        def on_year_change():
            sender = self.sender()
            if sender.count() == 0:
                return

            if sender == myComboBox_startTime_year:
                month = myComboBox_startTime_month
                day = myComboBox_startTime_day
                week = myComboBox_startTime_week
            elif sender == myComboBox_stopTime_year:
                month = myComboBox_stopTime_month
                day = myComboBox_stopTime_day
                week = myComboBox_stopTime_week
            else:
                return

            current_month = int(month.currentText())
            current_year = int(sender.currentText())

            if str(current_month) == '2':
                day.clear()
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    day.addItems(day_dict['闰月'])
                else:
                    day.addItems(day_dict['平月'])
            day_list_len = day.count()
            week.clear()
            mondays = []
            for y, m, d in [(current_year, current_month, int(x)) for x in range(1, day_list_len + 1)]:
                if datetime.datetime(y, m, d).strftime("%w") == '1':
                    mondays.append(d)
            weeks_list = []
            for d in mondays:
                sr = d
                sp = (d + 6) % (day_list_len)
                if sp == 0:
                    sp = day_list_len
                weeks_list.append("%d日~%d日" % (sr, sp))
            week.addItems(weeks_list)

        def on_month_change():
            sender = self.sender()
            if sender.count() == 0:
                return

            if sender == myComboBox_startTime_month:
                year = myComboBox_startTime_year
                day = myComboBox_startTime_day
                week = myComboBox_startTime_week
            elif sender == myComboBox_stopTime_month:
                year = myComboBox_stopTime_year
                day = myComboBox_stopTime_day
                week = myComboBox_stopTime_week
            else:
                return

            current_month = int(sender.currentText())
            current_year = int(year.currentText())

            day.clear()
            day_list = []
            if current_month == 2:
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    day_list = day_dict['闰月']
                else:
                    day_list = day_dict['平月']
            elif str(current_month) in month_dict['大月']:
                day_list = day_dict['大月']
            elif str(current_month) in month_dict['小月']:
                day_list = day_dict['小月']
            day.addItems(day_list)

            week.clear()
            mondays = []
            for y, m, d in [(current_year, current_month, int(x)) for x in day_list]:
                if datetime.datetime(y, m, d).strftime("%w") == '1':
                    mondays.append(d)
            weeks_list = []
            for d in mondays:
                sr = d
                sp = (d + 6) % (len(day_list))
                if sp == 0:
                    sp = len(day_list)
                weeks_list.append("%d日~%d日" % (sr, sp))
            week.addItems(weeks_list)

        pr = self
        month_component_list = [myComboBox_startTime_month, myComboBox_stopTime_month, myLabel_month, myLabel_month2]
        day_component_list = [myComboBox_startTime_day, myComboBox_stopTime_day, myLabel_day, myLabel_day2]
        week_component_list = [myComboBox_startTime_week, myComboBox_stopTime_week, myLabel_week, myLabel_week2]
        hour_component_list = [myComboBox_startTime_hour, myComboBox_stopTime_hour, myLabel_hour, myLabel_hour2]

        def selectionChange():
            if myComboBox_indexType.currentIndex() == 0:  # 指标类型是月
                # for x in month_component_list + day_component_list + hour_component_list:
                #     x.hide()
                for x in day_component_list + hour_component_list + week_component_list:
                    x.hide()
                for x in month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 1:  # 指标类型是周
                for x in hour_component_list + day_component_list:
                    x.hide()
                for x in week_component_list + month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 2:  # 指标类型是日
                for x in hour_component_list + week_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 3:  # 指标类型是小时
                for x in week_component_list:
                    x.hide()
                for x in month_component_list + day_component_list + hour_component_list:
                    x.show()

        myComboBox_startTime_year.currentIndexChanged.connect(on_year_change)
        myComboBox_startTime_month.currentIndexChanged.connect(on_month_change)
        myComboBox_stopTime_year.currentIndexChanged.connect(on_year_change)
        myComboBox_stopTime_month.currentIndexChanged.connect(on_month_change)
        myComboBox_indexType.currentIndexChanged.connect(selectionChange)
        self.all_component["uneven_watch"] = uneven_watch_component_dict

        for x in uneven_watch_component_dict:
            uneven_watch_component_dict[x].hide()

        pr = self

        def watchUnevenButtonSlot():
            timeType = myComboBox_indexType.currentText()

            def getTime(timeType):
                if timeType == "月":
                    start_time = myComboBox_startTime_year.currentText() + "%2d" % (
                        int(myComboBox_startTime_month.currentText()))
                    stop_time = myComboBox_stopTime_year.currentText() + "%2d" % (
                        int(myComboBox_stopTime_month.currentText()))
                    now_time = "%4d%2d" % (datetime.datetime.now().year, datetime.datetime.now().month)
                elif timeType == "日":
                    start_time = "%s%2d%2d" % (
                        myComboBox_startTime_year.currentText(), int(myComboBox_startTime_month.currentText()),
                        int(myComboBox_startTime_day.currentText()))
                    stop_time = "%s%2d%2d" % (
                        myComboBox_stopTime_year.currentText(), int(myComboBox_stopTime_month.currentText()),
                        int(myComboBox_stopTime_day.currentText()))
                    now_time = "%4d%2d%2d" % (
                        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                elif timeType == "周":
                    text1 = myComboBox_startTime_week.currentText()
                    text2 = myComboBox_stopTime_week.currentText()
                    start_day = int(text1.strip().split("日~")[0])
                    stop_day0 = int(text2.strip().split("日~")[0])
                    stop_day = int(text2.strip().split("日~")[-1][:-1])
                    print(text2.strip().split("日~")[-1], text2.strip().split("日~")[-1][:-1], stop_day0)
                    print(stop_day)
                    stop_month = int(myComboBox_stopTime_month.currentText())
                    stop_year = int(myComboBox_stopTime_year.currentText())
                    if stop_day <= stop_day0:
                        stop_month += 1
                        if stop_month > 12:
                            stop_month = stop_month % 12
                            stop_year += 1

                    start_time = "%s%2d%2d" % (
                        myComboBox_startTime_year.currentText(), int(myComboBox_startTime_month.currentText()),
                        int(start_day))
                    stop_time = "%4d%2d%2d" % (stop_year, stop_month, stop_day)
                    now_time = "%4d%2d%2d" % (
                        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                elif timeType == "小时":
                    start_time = "%s%2d%2d%2d" % (
                        myComboBox_startTime_year.currentText(), int(myComboBox_startTime_month.currentText()),
                        int(myComboBox_startTime_day.currentText()), int(myComboBox_startTime_hour.currentText()))
                    stop_time = "%s%2d%2d%2d" % (
                        myComboBox_stopTime_year.currentText(), int(myComboBox_stopTime_month.currentText()),
                        int(myComboBox_stopTime_day.currentText()), int(myComboBox_stopTime_hour.currentText()))
                    now_time = "%4d%2d%2d%2d" % (
                        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day,
                        datetime.datetime.now().hour)
                else:
                    raise RuntimeError("不存在的指标类型")

                return start_time, stop_time, now_time

            start_time, stop_time, now_time = getTime(timeType)
            # print(start_time, stop_time, now_time)
            if start_time > stop_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "开始时间不能大于结束时间", "确认")
            elif start_time > now_time or stop_time > now_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "不能选择未来的时间", "确认")
            else:
                user = get_user_by_id(pr.nowUserId)

                print(pr.nowUserId, timeType, start_time, stop_time)
                res = get_uneven_list(pr.nowUserId, timeType, start_time, stop_time)

                if res[0]:
                    uneven_list = res[1]
                    weather_list = []
                    if timeType == "日" or timeType == "周":
                        weather_list = get_weather_in_times_from_database(myComboBox_indexType.currentText(),
                                                                          int(start_time[:4]),
                                                                          int(start_time[4:6]), int(start_time[6:8]),
                                                                          int(stop_time[:4]), int(stop_time[4:6]),
                                                                          int(stop_time[6:8]))
                    elif timeType == "月":
                        weather_list = get_weather_in_times_from_database(myComboBox_indexType.currentText(),
                                                                          int(start_time[:4]),
                                                                          int(start_time[4:6]), 0, int(stop_time[:4]),
                                                                          int(stop_time[4:6]), 0)
                    # print(uneven_list, weather_list)

                    d = MyDialog(self)
                    user_content = get_user_by_id(self.nowUserId)
                    unit = user_content['gasUnit'] + '/' + user_content['userUnit'] + '·' + \
                           self.all_component['examine_index_result']['myComboBox_indexType'].currentText()
                    # temp_index_list = deepcopy(uneven_list)
                    # for row in temp_index_list:
                    #     row[1] = str(row[1]) + ' ' + unit
                    myTable_index = MyTable(d, uneven_list, ['日期', '不均匀系数'])
                    myTable_index.move(0, 0)

                    flag = True
                    for w in weather_list:
                        if len(w) <= 3:
                            flag = False
                    if not flag:
                        weather_list = []

                    myPlot_index = MyPlot(d, uneven_list, "", weather_list, '不均匀系数折线图')
                    myPlot_index.move(250, 0)
                    d.setWindowTitle("不均匀系数结果查看")
                    d.setWindowModality(QtCore.Qt.ApplicationModal)
                    d.exec_()

                else:
                    QtGui.QMessageBox.warning(pr, "出错", res[1], "确认")

        self.connect(myButton_export, QtCore.SIGNAL("clicked()"), watchUnevenButtonSlot)

    def uneven_search_fuc(self):
        uneven_search_component_dict = {}
        myLabel_indexType = MyLabel("系数类型 : ", self)
        myLabel_indexType.move(100, 60)
        uneven_search_component_dict["myLabel_indexType"] = myLabel_indexType

        myComboBox_indexType = MyComboBox(["月", "周", "日", "小时"], self)
        myComboBox_indexType.move(200, 60)
        uneven_search_component_dict["myComboBox_indexType"] = myComboBox_indexType

        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 120)
        uneven_search_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 120)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        uneven_search_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 180)
        uneven_search_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 180)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        uneven_search_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myLabel = MyLabel("时间 : ", self)
        myLabel.move(100, 240)
        uneven_search_component_dict["myLabel"] = myLabel

        myComboBox_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_year.move(200, 240)
        uneven_search_component_dict["myComboBox_year"] = myComboBox_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 240)
        myLabel_year.resize(50, 30)
        uneven_search_component_dict["myLabel_year"] = myLabel_year

        myComboBox_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_month.move(350, 240)
        uneven_search_component_dict["myComboBox_month"] = myComboBox_month
        myLabel_month = MyLabel(" 月", self)
        myLabel_month.move(450, 240)
        myLabel_month.resize(50, 30)
        uneven_search_component_dict["myLabel_month"] = myLabel_month

        myComboBox_day = MyComboBox([str(s) for s in range(1, 31)], self)
        myComboBox_day.move(500, 240)
        uneven_search_component_dict["myComboBox_day"] = myComboBox_day
        myLabel_day = MyLabel(" 日", self)
        myLabel_day.move(600, 240)
        myLabel_day.resize(50, 30)
        uneven_search_component_dict["myLabel_day"] = myLabel_day

        # myComboBox_week = MyComboBox([], self)
        # myComboBox_week.move(500, 240)
        # uneven_search_component_dict["myComboBox_week"] = myComboBox_week
        # myLabel_week = MyLabel(" 周", self)
        # myLabel_week.move(600, 240)
        # myLabel_week.resize(50, 30)
        # uneven_search_component_dict["myLabel_week"] = myLabel_week

        myComboBox_hour = MyComboBox([str(s) for s in range(1, 25)], self)
        myComboBox_hour.move(650, 240)
        uneven_search_component_dict["myComboBox_hour"] = myComboBox_hour
        myLabel_hour = MyLabel(" 小时", self)
        myLabel_hour.move(750, 240)
        myLabel_hour.resize(50, 30)
        uneven_search_component_dict["myLabel_hour"] = myLabel_hour

        myLabel_index = MyLabel('', self)
        myLabel_index.resize(500, 30)
        myLabel_index.move(600, 150)
        uneven_search_component_dict['myLabel_index'] = myLabel_index

        myButton_export = MyButton("查询", self)
        myButton_export.move(100, 300)
        uneven_search_component_dict["myButton_export"] = myButton_export

        month_dict = {'大月': ['1', '3', '5', '7', '8', '10', '12'], '小月': ['4', '6', '9', '11']}
        day_dict = {'小月': [str(x) for x in range(1, 31)], '大月': [str(x) for x in range(1, 32)],
                    '平月': [str(x) for x in range(1, 29)], '闰月': [str(x) for x in range(1, 30)]}

        def on_year_change():
            sender = self.sender()
            if sender.count() == 0:
                return

            month = myComboBox_month
            day = myComboBox_day
            # week = myComboBox_week

            current_month = int(month.currentText())
            current_year = int(sender.currentText())

            if str(current_month) == '2':
                day.clear()
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    day.addItems(day_dict['闰月'])
                else:
                    day.addItems(day_dict['平月'])
            day_list_len = day.count()
            # week.clear()
            # mondays = []
            # for y, m, d in [(current_year, current_month, int(x)) for x in range(1, day_list_len + 1)]:
            #     if datetime.datetime(y, m, d).strftime("%w") == '1':
            #         mondays.append(d)
            # weeks_list = []
            # for d in mondays:
            #     sr = d
            #     sp = (d + 6) % (day_list_len)
            #     if sp == 0:
            #         sp = day_list_len
            #     weeks_list.append("%d日~%d日" % (sr, sp))
            # week.addItems(weeks_list)

        def on_month_change():
            sender = self.sender()
            if sender.count() == 0:
                return

            year = myComboBox_year
            day = myComboBox_day
            # week = myComboBox_week

            current_month = int(sender.currentText())
            current_year = int(year.currentText())

            day.clear()
            day_list = []
            if current_month == 2:
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    day_list = day_dict['闰月']
                else:
                    day_list = day_dict['平月']
            elif str(current_month) in month_dict['大月']:
                day_list = day_dict['大月']
            elif str(current_month) in month_dict['小月']:
                day_list = day_dict['小月']
            day.addItems(day_list)

            # week.clear()
            # mondays = []
            # for y, m, d in [(current_year, current_month, int(x)) for x in day_list]:
            #     if datetime.datetime(y, m, d).strftime("%w") == '1':
            #         mondays.append(d)
            # weeks_list = []
            # for d in mondays:
            #     sr = d
            #     sp = (d + 6) % (len(day_list))
            #     if sp == 0:
            #         sp = len(day_list)
            #     weeks_list.append("%d日~%d日" % (sr, sp))
            # week.addItems(weeks_list)

        pr = self
        month_component_list = [myComboBox_month, myLabel_month]
        day_component_list = [myComboBox_day, myLabel_day]
        # week_component_list = [myComboBox_week, myLabel_week]
        hour_component_list = [myComboBox_hour, myLabel_hour]

        def selectionChange():
            if myComboBox_indexType.currentIndex() == 0:  # 指标类型是月
                # for x in month_component_list + day_component_list + hour_component_list:
                #     x.hide()
                for x in day_component_list + hour_component_list:
                    x.hide()
                for x in month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 1:  # 指标类型是周
                for x in hour_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 2:  # 指标类型是日  + week_component_list
                for x in hour_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif myComboBox_indexType.currentIndex() == 3:  # 指标类型是小时
                # for x in week_component_list:
                #     x.hide()
                for x in month_component_list + day_component_list + hour_component_list:
                    x.show()

        myComboBox_year.currentIndexChanged.connect(on_year_change)
        myComboBox_month.currentIndexChanged.connect(on_month_change)
        myComboBox_indexType.currentIndexChanged.connect(selectionChange)
        self.all_component["uneven_search"] = uneven_search_component_dict

        for x in uneven_search_component_dict:
            uneven_search_component_dict[x].hide()

        pr = self

        def dataExportButtonSlot():
            timeType = myComboBox_indexType.currentText()

            def getTime(timeType):
                if timeType == "月":
                    start_time = myComboBox_year.currentText() + "%2d" % (
                        int(myComboBox_month.currentText()))
                    now_time = "%4d%2d" % (datetime.datetime.now().year, datetime.datetime.now().month)
                elif timeType == "日":
                    start_time = "%s%2d%2d" % (
                        myComboBox_year.currentText(), int(myComboBox_month.currentText()),
                        int(myComboBox_day.currentText()))
                    now_time = "%4d%2d%2d" % (
                        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                elif timeType == "周":
                    start_time = "%s%2d%2d" % (
                        myComboBox_year.currentText(), int(myComboBox_month.currentText()),
                        int(myComboBox_day.currentText()))
                    now_time = "%4d%2d%2d" % (
                        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                    # text1 = myComboBox_week.currentText()
                    # start_day = int(text1.strip().split("日~")[0])
                    # stop_day = int(text1.strip().split("日~")[-1][:-1])
                    # stop_month = int(myComboBox_month.currentText())
                    # stop_year = int(myComboBox_year.currentText())
                    # if stop_day >= start_day:
                    #     stop_month += 1
                    #     if stop_month > 12:
                    #         stop_month = stop_month % 12
                    #         stop_year += 1
                    #
                    # start_time = "%s%2d%2d" % (
                    #     myComboBox_year.currentText(), int(myComboBox_month.currentText()), int(start_day))
                    # stop_time = "%4d%2d%2d" % (stop_year, stop_month, stop_day)
                    # start_time += stop_time
                    # now_time = "%4d%2d%2d" % (
                    # datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)

                elif timeType == "小时":
                    start_time = "%s%2d%2d%2d" % (
                        myComboBox_year.currentText(), int(myComboBox_month.currentText()),
                        int(myComboBox_day.currentText()), int(myComboBox_hour.currentText()))
                    now_time = "%4d%2d%2d%2d" % (
                        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day,
                        datetime.datetime.now().hour)
                else:
                    raise RuntimeError("不存在的指标类型")

                return start_time, now_time

            start_time, now_time = getTime(timeType)
            # print(start_time, now_time)
            if start_time > now_time:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "不能选择未来的时间", "确认")
            else:
                res = search_uneven(pr.nowUserId, timeType, start_time)
                if res[0]:

                    userType = myComboBox_userType.currentText()
                    userName = myComboBox_userName.currentText()
                    # print((userType, userName, start_time, timeType, res))
                    myLabel_index.setText("%s-%s用户的%s不均匀系数为%s" % (userType, userName, timeType, res[1]))
                else:
                    QtGui.QMessageBox.warning(pr, "查询失败", res[1], "确认")
        self.connect(myButton_export, QtCore.SIGNAL("clicked()"), dataExportButtonSlot)

    def human_predict_fuc(self):
        human_predict_component_dict = {}
        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 60)
        human_predict_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        human_predict_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 120)
        human_predict_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 120)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        human_predict_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myLabel_high = MyLabel("高方案增长百分比 : ", self)
        myLabel_high.move(100, 180)
        myLabel_high.resize(150, 30)
        human_predict_component_dict['myLabel_high'] = myLabel_high

        myLineEdit_high = MyLineEdit(self)
        myLineEdit_high.move(250, 180)
        human_predict_component_dict['myLineEdit_high'] = myLineEdit_high
        myLabel_percent0 = MyLabel(" %", self)
        myLabel_percent0.move(351, 180)
        myLabel_percent0.resize(50, 30)
        human_predict_component_dict["myLabel_percent0"] = myLabel_percent0

        myLabel_mid = MyLabel("中方案增长百分比 : ", self)
        myLabel_mid.move(100, 240)
        myLabel_mid.resize(150, 30)
        human_predict_component_dict['myLabel_mid'] = myLabel_mid

        myLineEdit_mid = MyLineEdit(self)
        myLineEdit_mid.move(250, 240)
        human_predict_component_dict['myLineEdit_mid'] = myLineEdit_mid
        myLabel_percent1 = MyLabel(" %", self)
        myLabel_percent1.move(351, 240)
        myLabel_percent1.resize(50, 30)
        human_predict_component_dict["myLabel_percent1"] = myLabel_percent1

        myLabel_low = MyLabel("低方案增长百分比 : ", self)
        myLabel_low.move(100, 300)
        myLabel_low.resize(150, 30)
        human_predict_component_dict['myLabel_low'] = myLabel_low

        myLineEdit_low = MyLineEdit(self)
        myLineEdit_low.move(250, 300)
        human_predict_component_dict['myLineEdit_low'] = myLineEdit_low
        myLabel_percent2 = MyLabel(" %", self)
        myLabel_percent2.move(351, 300)
        myLabel_percent2.resize(50, 30)
        human_predict_component_dict["myLabel_percent2"] = myLabel_percent2

        myLabel_startTime = MyLabel("开始日期 : ", self)
        myLabel_startTime.move(100, 360)
        human_predict_component_dict["myLabel_startTime"] = myLabel_startTime

        myComboBox_startTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_startTime_year.move(200, 360)
        human_predict_component_dict["myComboBox_startTime_year"] = myComboBox_startTime_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 360)
        myLabel_year.resize(50, 30)
        human_predict_component_dict["myLabel_year"] = myLabel_year

        myLabel_stopTime = MyLabel("结束日期 : ", self)
        myLabel_stopTime.move(350, 360)
        human_predict_component_dict["myLabel_stopTime"] = myLabel_stopTime

        myComboBox_stopTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_stopTime_year.move(450, 360)
        human_predict_component_dict["myComboBox_stopTime_year"] = myComboBox_stopTime_year
        myLabel_year2 = MyLabel(" 年", self)
        myLabel_year2.move(550, 360)
        myLabel_year2.resize(50, 30)
        human_predict_component_dict["myLabel_year2"] = myLabel_year2

        myButton_predict = MyButton("预测", self)
        myButton_predict.move(100, 420)
        human_predict_component_dict["myButton_predict"] = myButton_predict

        self.all_component["human_predict"] = human_predict_component_dict

        for x in human_predict_component_dict:
            human_predict_component_dict[x].hide()

        pr = self

        def predictButtonSlot():
            start_year = int(myComboBox_startTime_year.currentText())
            stop_year = int(myComboBox_stopTime_year.currentText())
            high = myLineEdit_high.text()
            mid = myLineEdit_mid.text()
            low = myLineEdit_low.text()

            if start_year > stop_year:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "开始时间不能大于结束时间", "确认")
            elif not (high and mid and low):
                QtGui.QMessageBox.warning(pr, "输入不全", "某方案增长比未填写", "确认")
            elif not (high.isdigit() and mid.isdigit() and low.isdigit()):
                QtGui.QMessageBox.warning(pr, "输入有误", "某方案增长百分比不是整数", "确认")
            else:
                def strfList(l):
                    return [str(x) for x in l]

                user_content = get_user_by_id(pr.nowUserId)
                res = human_predict_userNum(pr.nowUserId, start_year, stop_year, float(high) * 0.01, float(mid) * 0.01,
                                            float(low) * 0.01)
                if res[0]:
                    high_dict, mid_dict, low_dict = res[1]
                    year_list = list(range(start_year, stop_year + 1))
                    d = MyDialog(self)
                    userUnit = user_content["userUnit"]
                    column_title = ['用户规模（%s）' % userUnit] + ["%d年" % y for y in year_list]
                    data_list = [["高方案预测数据："] + strfList(high_dict), ["中方案预测数据："] + strfList(mid_dict),
                                 ["低方案预测数据："] + strfList(low_dict)]
                    print(data_list, column_title)
                    myTable_index = MyTable(d, data_list, column_title)
                    myTable_index.resize(view_setting["BigTableWidth"], view_setting["BigTableHeight"])
                    myTable_index.move(0, 0)
                    myTable_index.resizeColumnsToContents()
                    myTable_index.resizeRowsToContents()
                    d.setWindowTitle("预测结果")
                    d.setWindowModality(QtCore.Qt.ApplicationModal)
                    d.exec_()

                else:
                    QtGui.QMessageBox.warning(pr, "预测失败", res[1], "确认")

        self.connect(myButton_predict, QtCore.SIGNAL("clicked()"), predictButtonSlot)

    def model_predict_fuc(self):
        model_predict_component_dict = {}
        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 60)
        model_predict_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        model_predict_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 120)
        model_predict_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 120)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        model_predict_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myLabel_model = MyLabel("模型选择 : ", self)
        myLabel_model.move(100, 180)
        model_predict_component_dict["myLabel_model"] = myLabel_model

        myComboBox_model = MyComboBox(["线性回归模型", "多项式回归模型", "对数回归模型", "灰色模型"], self)
        myComboBox_model.move(200, 180)
        model_predict_component_dict["myComboBox_model"] = myComboBox_model

        myLabel_startTime = MyLabel("开始日期 : ", self)
        myLabel_startTime.move(100, 240)
        model_predict_component_dict["myLabel_startTime"] = myLabel_startTime

        myComboBox_startTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_startTime_year.move(200, 240)
        model_predict_component_dict["myComboBox_startTime_year"] = myComboBox_startTime_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 240)
        myLabel_year.resize(50, 30)
        model_predict_component_dict["myLabel_year"] = myLabel_year

        myLabel_stopTime = MyLabel("结束日期 : ", self)
        myLabel_stopTime.move(350, 240)
        model_predict_component_dict["myLabel_stopTime"] = myLabel_stopTime

        myComboBox_stopTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_stopTime_year.move(450, 240)
        model_predict_component_dict["myComboBox_stopTime_year"] = myComboBox_stopTime_year
        myLabel_year2 = MyLabel(" 年", self)
        myLabel_year2.move(550, 240)
        myLabel_year2.resize(50, 30)
        model_predict_component_dict["myLabel_year2"] = myLabel_year2

        myButton_predict = MyButton("预测", self)
        myButton_predict.move(100, 300)
        model_predict_component_dict["myButton_predict"] = myButton_predict

        self.all_component["model_predict"] = model_predict_component_dict

        for x in model_predict_component_dict:
            model_predict_component_dict[x].hide()

        pr = self

        def predictButtonSlot():
            start_year = int(myComboBox_startTime_year.currentText())
            stop_year = int(myComboBox_stopTime_year.currentText())
            model_type = myComboBox_model.currentIndex()

            if start_year > stop_year:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "开始时间不能大于结束时间", "确认")
            else:
                def strfList(l):
                    return [str(x) for x in l]

                user_content = get_user_by_id(pr.nowUserId)
                res = model_predict_userNum(pr.nowUserId, start_year, stop_year, model_type)
                if res[0]:
                    predict_result = res[1]
                    year_list = list(range(start_year, stop_year + 1))
                    d = MyDialog(self)
                    userUnit = user_content["userUnit"]
                    column_title = ["年份"] + ["%d年" % y for y in year_list]
                    data_list = [['用户数量（%s）' % userUnit] + strfList(predict_result)]
                    print(data_list, column_title)
                    myTable_index = MyTable(d, data_list, column_title)
                    myTable_index.resize(view_setting["BigTableWidth"], view_setting["BigTableHeight"])
                    myTable_index.move(0, 0)
                    myTable_index.resizeColumnsToContents()
                    myTable_index.resizeRowsToContents()
                    d.setWindowTitle("预测结果")
                    d.setWindowModality(QtCore.Qt.ApplicationModal)
                    d.exec_()

                else:
                    QtGui.QMessageBox.warning(pr, "预测失败", res[1], "确认")

        self.connect(myButton_predict, QtCore.SIGNAL("clicked()"), predictButtonSlot)

    def index_predict_fuc(self):
        index_predict_component_dict = {}
        myLabel_userType = MyLabel("用户类型 : ", self)
        myLabel_userType.move(100, 60)
        index_predict_component_dict["myLabel_userType"] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 60)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        index_predict_component_dict["myComboBox_userType"] = myComboBox_userType

        myLabel_userName = MyLabel("用户名称 : ", self)
        myLabel_userName.move(100, 120)
        index_predict_component_dict["myLabel_userName"] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 120)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        index_predict_component_dict["myComboBox_userName"] = myComboBox_userName

        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        myLabel_indexType = MyLabel("指标类型 : ", self)
        myLabel_indexType.move(100, 180)
        index_predict_component_dict["myLabel_indexType"] = myLabel_indexType

        myComboBox_indexType = MyComboBox(["年", "月"], self)
        myComboBox_indexType.move(200, 180)
        index_predict_component_dict["myComboBox_indexType"] = myComboBox_indexType

        myLabel_model = MyLabel("模型选择 : ", self)
        myLabel_model.move(100, 240)
        index_predict_component_dict["myLabel_model"] = myLabel_model

        myComboBox_model = MyComboBox(["指数平滑", "灰色模型", "回归分析"], self)
        myComboBox_model.move(200, 240)
        index_predict_component_dict["myComboBox_model"] = myComboBox_model

        myLabel_startTime = MyLabel("开始日期 : ", self)
        myLabel_startTime.move(100, 300)
        index_predict_component_dict["myLabel_startTime"] = myLabel_startTime

        myComboBox_startTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_startTime_year.move(200, 300)
        index_predict_component_dict["myComboBox_startTime_year"] = myComboBox_startTime_year
        myLabel_year = MyLabel(" 年", self)
        myLabel_year.move(300, 300)
        myLabel_year.resize(50, 30)
        index_predict_component_dict["myLabel_year"] = myLabel_year

        myComboBox_startTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_startTime_month.move(350, 300)
        index_predict_component_dict["myComboBox_startTime_month"] = myComboBox_startTime_month
        myLabel_month = MyLabel(" 月", self)
        myLabel_month.move(450, 300)
        myLabel_month.resize(50, 30)
        index_predict_component_dict["myLabel_month"] = myLabel_month

        myLabel_stopTime = MyLabel("结束日期 : ", self)
        myLabel_stopTime.move(100, 360)
        index_predict_component_dict["myLabel_stopTime"] = myLabel_stopTime

        myComboBox_stopTime_year = MyComboBox([str(s) for s in range(2000, 2051)], self)
        myComboBox_stopTime_year.move(200, 360)
        index_predict_component_dict["myComboBox_stopTime_year"] = myComboBox_stopTime_year
        myLabel_year2 = MyLabel(" 年", self)
        myLabel_year2.move(300, 360)
        myLabel_year2.resize(50, 30)
        index_predict_component_dict["myLabel_year2"] = myLabel_year2
        myComboBox_stopTime_month = MyComboBox([str(s) for s in range(1, 13)], self)
        myComboBox_stopTime_month.move(350, 360)
        index_predict_component_dict["myComboBox_stopTime_month"] = myComboBox_stopTime_month
        myLabel_month2 = MyLabel(" 月", self)
        myLabel_month2.move(450, 360)
        myLabel_month2.resize(50, 30)
        index_predict_component_dict["myLabel_month2"] = myLabel_month2

        def selectionChange():
            if pr.all_component["index_predict"]["myComboBox_indexType"].currentIndex() == 0:  # 指标类型是年
                pr.all_component["index_predict"]["myComboBox_startTime_month"].hide()
                pr.all_component["index_predict"]["myComboBox_stopTime_month"].hide()
                pr.all_component["index_predict"]["myLabel_month"].hide()
                pr.all_component["index_predict"]["myLabel_month2"].hide()
                myComboBox_model.clear()
                myComboBox_model.addItems(["指数平滑", "灰色模型", "回归分析"])
            elif pr.all_component["index_predict"]["myComboBox_indexType"].currentIndex() == 1:  # 指标类型是月
                pr.all_component["index_predict"]["myComboBox_startTime_month"].show()
                pr.all_component["index_predict"]["myComboBox_stopTime_month"].show()
                pr.all_component["index_predict"]["myLabel_month"].show()
                pr.all_component["index_predict"]["myLabel_month2"].show()
                myComboBox_model.clear()
                myComboBox_model.addItems(["指数平滑", "灰色模型", "回归分析"])

        myComboBox_indexType.currentIndexChanged.connect(selectionChange)

        myButton_predict = MyButton("预测", self)
        myButton_predict.move(100, 420)
        index_predict_component_dict["myButton_predict"] = myButton_predict

        self.all_component["index_predict"] = index_predict_component_dict

        for x in index_predict_component_dict:
            index_predict_component_dict[x].hide()

        pr = self

        def predictButtonSlot():
            start_year = int(myComboBox_startTime_year.currentText())
            stop_year = int(myComboBox_stopTime_year.currentText())
            start_month = int(myComboBox_startTime_month.currentText())
            stop_month = int(myComboBox_stopTime_month.currentText())
            timeType = myComboBox_indexType.currentText()
            model_type = myComboBox_model.currentIndex()

            if start_year > stop_year:
                QtGui.QMessageBox.warning(pr, "日期选择有误", "开始时间不能大于结束时间", "确认")
            else:
                def strfList(l):
                    return [str(x) for x in l]

                param = ""
                if model_type == 0:  # 二次指数平滑
                    text, ok = QtGui.QInputDialog.getText(pr, '请输入α平滑常数', '1.时间序列比较平稳时，选择较小的α值，0.05-0.20\n' + \
                                                          "2.时间序列有波动，但长期趋势没大的变化，可选稍大的α值，0.10-0.40。\n" + \
                                                          "3.时间序列波动很大，长期趋势变化大有明显的上升或下降趋势时，宜选较大的α值，0.60-0.80。\n" + \
                                                          "4.当时间序列是上升或下降序列，满足加性模型，α取较大值，0.60-1。\n")
                    if ok:
                        param = text
                    else:
                        QtGui.QMessageBox.warning(pr, "无法预测", "未输入α平滑常数", "确认")
                        return
                elif timeType == "月" and model_type == 2:  # 月 回归分析
                    text, ok = QtGui.QInputDialog.getText(pr, '请输入温度', '请输入要预测月份的平均温度')
                    if ok:
                        param = text
                    else:
                        QtGui.QMessageBox.warning(pr, "无法预测", "未输入该月份温度", "确认")
                        return

                user_content = get_user_by_id(pr.nowUserId)
                unit = "%s / %s · %s" % (user_content["gasUnit"], user_content["userUnit"], timeType)
                res = model_predict_gasIndex(pr.nowUserId, start_year, start_month, stop_year, stop_month, timeType,
                                             model_type, param)
                if res[0]:
                    predict_result = res[1]
                    time_list = [t[0] for t in predict_result]
                    index_list = [t[1] for t in predict_result]
                    d = MyDialog(self)
                    column_title = ["时间"] + ["%s" % y for y in time_list]
                    data_list = [['用气指标（%s）' % unit] + strfList(index_list)]
                    print(data_list)
                    print(column_title)
                    myTable_index = MyTable(d, data_list, column_title)
                    myTable_index.resize(view_setting["BigTableWidth"], view_setting["BigTableHeight"])
                    myTable_index.move(0, 0)
                    myTable_index.resizeColumnsToContents()
                    myTable_index.resizeRowsToContents()
                    d.setWindowTitle("预测结果")
                    d.setWindowModality(QtCore.Qt.ApplicationModal)
                    d.exec_()

                else:
                    QtGui.QMessageBox.warning(pr, "预测失败", res[1], "确认")

        self.connect(myButton_predict, QtCore.SIGNAL("clicked()"), predictButtonSlot)


    def selectionchange(self):
        sender = self.sender()
        # print(sender)
        reciever = self.comboBoxPair[sender]
        # print("allcount:" + str(reciever.count()))

        reciever.clear()

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
            now_userName = sender.currentText()
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
        d = MyDialog(self)

        myLabel_title = MyLabel(userContent['userType'] + '-' + userContent['userName'] + '用户：', d)
        myLabel_title.move(100, 60)

        myLabel_gasCondition = MyLabel('用气工况：', d)
        myLabel_gasCondition.move(100, 120)

        def on_year_change():
            if myComboBox_month.currentIndex() == 2:
                current_year = int(myComboBox_year.currentText())
                myComboBox_day.clear()
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    myComboBox_day.addItems(day_dict['闰月'])
                else:
                    myComboBox_day.addItems(day_dict['平月'])

        myComboBox_year = MyComboBox([str(x) for x in range(2000, 2051)], d)
        myComboBox_year.move(200, 120)
        myComboBox_year.currentIndexChanged.connect(on_year_change)

        myLabel_year = MyLabel('年', d)
        myLabel_year.move(300, 120)

        def on_month_change():
            if myComboBox_month.currentIndex() == 0:
                myComboBox_day.clear()
                myComboBox_hour.clear()
                return
            current_month = myComboBox_month.currentText()
            myComboBox_day.clear()
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

        myComboBox_month = MyComboBox([''] + [str(x) for x in range(1, 13)], d)
        myComboBox_month.move(320, 120)
        myComboBox_month.currentIndexChanged.connect(on_month_change)

        myLabel_month = MyLabel('月', d)
        myLabel_month.move(420, 120)

        def on_day_change():
            if myComboBox_day.currentIndex() == 0 or myComboBox_day.currentIndex() == -1:
                myComboBox_hour.clear()
            elif myComboBox_hour.count() == 0:
                myComboBox_hour.addItems([''] + [str(x) for x in range(1, 25)])
        myComboBox_day = MyComboBox([], d)
        myComboBox_day.move(440, 120)
        myComboBox_day.currentIndexChanged.connect(on_day_change)

        myLabel_day = MyLabel('日', d)
        myLabel_day.move(540, 120)
        myComboBox_hour = MyComboBox([], d)
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
            year = 2000 + myComboBox_year.currentIndex()
            month = myComboBox_month.currentIndex()
            day = myComboBox_day.currentIndex()
            hour = myComboBox_hour.currentIndex()
            if gasNum == '':
                QtGui.QMessageBox.warning(d, "数据录入失败", "用气量不能为空！", "确定")
                return
            if userNum == '':
                QtGui.QMessageBox.warning(d, "数据录入失败", "用户数不能为空！", "确定")
                return
            try:
                gasNum = float(gasNum)
                userNum = int(userNum)
                add_user_data(userId, gasNum, userNum, year, month, day, hour)
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
        cb.clear()
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

    def display_dataExport_uneven(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()

        for x in self.all_component['dataExport_uneven']:
            self.all_component['dataExport_uneven'][x].show()

        def selectionChange():
            month_component_list = [self.all_component["dataExport_uneven"]["myComboBox_startTime_month"],
                                    self.all_component["dataExport_uneven"]["myComboBox_stopTime_month"],
                                    self.all_component["dataExport_uneven"]["myLabel_month"],
                                    self.all_component["dataExport_uneven"]["myLabel_month2"]]
            day_component_list = [self.all_component["dataExport_uneven"]["myComboBox_startTime_day"],
                                  self.all_component["dataExport_uneven"]["myComboBox_stopTime_day"],
                                  self.all_component["dataExport_uneven"]["myLabel_day"],
                                  self.all_component["dataExport_uneven"]["myLabel_day2"]]
            week_component_list = [self.all_component["dataExport_uneven"]["myComboBox_startTime_week"],
                                   self.all_component["dataExport_uneven"]["myComboBox_stopTime_week"],
                                   self.all_component["dataExport_uneven"]["myLabel_week"],
                                   self.all_component["dataExport_uneven"]["myLabel_week2"]]
            hour_component_list = [self.all_component["dataExport_uneven"]["myComboBox_startTime_hour"],
                                   self.all_component["dataExport_uneven"]["myComboBox_stopTime_hour"],
                                   self.all_component["dataExport_uneven"]["myLabel_hour"],
                                   self.all_component["dataExport_uneven"]["myLabel_hour2"]]
            currentIndex = self.all_component["dataExport_uneven"]["myComboBox_indexType"].currentIndex()
            if currentIndex == 0:  # 指标类型是月
                # for x in month_component_list + day_component_list + hour_component_list:
                #     x.hide()
                for x in day_component_list + hour_component_list + week_component_list:
                    x.hide()
                for x in month_component_list:
                    x.show()
            elif currentIndex == 1:  # 指标类型是周
                for x in hour_component_list + day_component_list:
                    x.hide()
                for x in week_component_list + month_component_list:
                    x.show()
            elif currentIndex == 2:  # 指标类型是日
                for x in hour_component_list + week_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif currentIndex == 3:  # 指标类型是小时
                for x in week_component_list:
                    x.hide()
                for x in month_component_list + day_component_list + hour_component_list:
                    x.show()

        selectionChange()

        cb = self.all_component["dataExport_uneven"]["myComboBox_startTime_year"]
        cb.clear()
        cb.addItems([str(x) for x in range(2000, 2051)])
        cb = self.all_component["dataExport_uneven"]["myComboBox_stopTime_year"]
        cb.clear()
        cb.addItems([str(x) for x in range(2000, 2051)])
        cb = self.all_component["dataExport_uneven"]["myComboBox_startTime_month"]
        cb.clear()
        cb.addItems([str(x) for x in range(1, 13)])
        cb = self.all_component["dataExport_uneven"]["myComboBox_stopTime_month"]
        cb.clear()
        cb.addItems([str(x) for x in range(1, 13)])

        userType_list = get_all_userType()
        cb = self.all_component["dataExport_uneven"]["myComboBox_userType"]
        cb.clear()
        cb.addItems(userType_list)

    def display_uneven_search(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()

        for x in self.all_component['uneven_search']:
            self.all_component['uneven_search'][x].show()

        def selectionChange():
            month_component_list = [self.all_component["uneven_search"]["myComboBox_month"],
                                    self.all_component["uneven_search"]["myLabel_month"], ]
            day_component_list = [self.all_component["uneven_search"]["myComboBox_day"],
                                  self.all_component["uneven_search"]["myLabel_day"], ]
            # week_component_list = [self.all_component["uneven_search"]["myComboBox_week"],
            #                        self.all_component["uneven_search"]["myLabel_week"], ]
            hour_component_list = [self.all_component["uneven_search"]["myComboBox_hour"],
                                   self.all_component["uneven_search"]["myLabel_hour"], ]
            currentIndex = self.all_component["uneven_search"]["myComboBox_indexType"].currentIndex()
            if currentIndex == 0:  # 指标类型是月
                # for x in month_component_list + day_component_list + hour_component_list:
                #     x.hide()
                for x in day_component_list + hour_component_list:
                    x.hide()
                for x in month_component_list:
                    x.show()
            elif currentIndex == 1:  # 指标类型是周
                for x in hour_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif currentIndex == 2:  # 指标类型是日
                for x in hour_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif currentIndex == 3:  # 指标类型是小时
                # for x in week_component_list:
                #     x.hide()
                for x in month_component_list + day_component_list + hour_component_list:
                    x.show()

        selectionChange()

        cb = self.all_component["uneven_search"]["myComboBox_year"]
        cb.clear()
        cb.addItems([str(x) for x in range(2000, 2051)])
        cb = self.all_component["uneven_search"]["myComboBox_month"]
        cb.clear()
        cb.addItems([str(x) for x in range(1, 13)])

        userType_list = get_all_userType()
        cb = self.all_component["uneven_search"]["myComboBox_userType"]
        cb.clear()
        cb.addItems(userType_list)

        self.all_component["uneven_search"]["myLabel_index"].setText("")

    def display_uneven_watch(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()

        for x in self.all_component['uneven_watch']:
            self.all_component['uneven_watch'][x].show()

        def selectionChange():
            month_component_list = [self.all_component["uneven_watch"]["myComboBox_startTime_month"],
                                    self.all_component["uneven_watch"]["myComboBox_stopTime_month"],
                                    self.all_component["uneven_watch"]["myLabel_month"],
                                    self.all_component["uneven_watch"]["myLabel_month2"]]
            day_component_list = [self.all_component["uneven_watch"]["myComboBox_startTime_day"],
                                  self.all_component["uneven_watch"]["myComboBox_stopTime_day"],
                                  self.all_component["uneven_watch"]["myLabel_day"],
                                  self.all_component["uneven_watch"]["myLabel_day2"]]
            week_component_list = [self.all_component["uneven_watch"]["myComboBox_startTime_week"],
                                   self.all_component["uneven_watch"]["myComboBox_stopTime_week"],
                                   self.all_component["uneven_watch"]["myLabel_week"],
                                   self.all_component["uneven_watch"]["myLabel_week2"]]
            hour_component_list = [self.all_component["uneven_watch"]["myComboBox_startTime_hour"],
                                   self.all_component["uneven_watch"]["myComboBox_stopTime_hour"],
                                   self.all_component["uneven_watch"]["myLabel_hour"],
                                   self.all_component["uneven_watch"]["myLabel_hour2"]]
            currentIndex = self.all_component["uneven_watch"]["myComboBox_indexType"].currentIndex()
            if currentIndex == 0:  # 指标类型是月
                # for x in month_component_list + day_component_list + hour_component_list:
                #     x.hide()
                for x in day_component_list + hour_component_list + week_component_list:
                    x.hide()
                for x in month_component_list:
                    x.show()
            elif currentIndex == 1:  # 指标类型是周
                for x in hour_component_list + day_component_list:
                    x.hide()
                for x in week_component_list + month_component_list:
                    x.show()
            elif currentIndex == 2:  # 指标类型是日
                for x in hour_component_list + week_component_list:
                    x.hide()
                for x in day_component_list + month_component_list:
                    x.show()
            elif currentIndex == 3:  # 指标类型是小时
                for x in week_component_list:
                    x.hide()
                for x in month_component_list + day_component_list + hour_component_list:
                    x.show()

        selectionChange()

        cb = self.all_component["uneven_watch"]["myComboBox_startTime_year"]
        cb.clear()
        cb.addItems([str(x) for x in range(2000, 2051)])
        cb = self.all_component["uneven_watch"]["myComboBox_stopTime_year"]
        cb.clear()
        cb.addItems([str(x) for x in range(2000, 2051)])
        cb = self.all_component["uneven_watch"]["myComboBox_startTime_month"]
        cb.clear()
        cb.addItems([str(x) for x in range(1, 13)])
        cb = self.all_component["uneven_watch"]["myComboBox_stopTime_month"]
        cb.clear()
        cb.addItems([str(x) for x in range(1, 13)])

        userType_list = get_all_userType()
        cb = self.all_component["uneven_watch"]["myComboBox_userType"]
        cb.clear()
        cb.addItems(userType_list)

    def display_human_predict(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        userType_list = get_all_userType()

        cb = self.all_component["human_predict"]["myComboBox_userType"]
        cb.clear()
        cb.addItems(userType_list)

        for x in self.all_component['human_predict']:
            self.all_component['human_predict'][x].show()

    def display_model_predict(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()
        userType_list = get_all_userType()

        cb = self.all_component["model_predict"]["myComboBox_userType"]
        cb.clear()
        cb.addItems(userType_list)

        for x in self.all_component['model_predict']:
            self.all_component['model_predict'][x].show()

    def display_index_predict(self):
        for k in self.all_component:
            for x in self.all_component[k]:
                self.all_component[k][x].hide()

        userType_list = get_all_userType()
        cb = self.all_component["index_predict"]["myComboBox_userType"]
        cb.clear()
        cb.addItems(userType_list)

        for x in self.all_component['index_predict']:
            self.all_component['index_predict'][x].show()

        pr = self

        def selectionChange():
            if pr.all_component["index_predict"]["myComboBox_indexType"].currentIndex() == 0:  # 指标类型是年
                pr.all_component["index_predict"]["myComboBox_startTime_month"].hide()
                pr.all_component["index_predict"]["myComboBox_stopTime_month"].hide()
                pr.all_component["index_predict"]["myLabel_month"].hide()
                pr.all_component["index_predict"]["myLabel_month2"].hide()
                pr.all_component["index_predict"]["myComboBox_model"].clear()
                pr.all_component["index_predict"]["myComboBox_model"].addItems(["指数平滑", "灰色模型", "回归分析"])
            elif pr.all_component["index_predict"]["myComboBox_indexType"].currentIndex() == 1:  # 指标类型是月
                pr.all_component["index_predict"]["myComboBox_startTime_month"].show()
                pr.all_component["index_predict"]["myComboBox_stopTime_month"].show()
                pr.all_component["index_predict"]["myLabel_month"].show()
                pr.all_component["index_predict"]["myLabel_month2"].show()
                pr.all_component["index_predict"]["myComboBox_model"].clear()
                pr.all_component["index_predict"]["myComboBox_model"].addItems(["指数平滑", "灰色模型", "回归分析"])

        selectionChange()

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
            if myComboBox_month.currentIndex() == 2:
                current_year = int(myComboBox_year.currentText())
                myComboBox_day.clear()
                if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                    myComboBox_day.addItems(day_dict['闰月'])
                else:
                    myComboBox_day.addItems(day_dict['平月'])

        myComboBox_year = MyComboBox([str(x) for x in range(2000, 2051)], d)
        myComboBox_year.move(200, 180)
        myComboBox_year.currentIndexChanged.connect(on_year_change)

        myLabel_year = MyLabel('年', d)
        myLabel_year.move(300, 180)

        def on_month_change():
            if myComboBox_month.currentIndex() == 0:
                myComboBox_day.clear()
                myComboBox_hour.clear()
                return
            current_month = myComboBox_month.currentText()
            myComboBox_day.clear()
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

        myComboBox_month = MyComboBox([''] + [str(x) for x in range(1, 13)], d)
        myComboBox_month.move(320, 180)
        myComboBox_month.currentIndexChanged.connect(on_month_change)

        myLabel_month = MyLabel('月', d)
        myLabel_month.move(420, 180)

        def on_day_change():
            if myComboBox_day.currentIndex() == 0 or myComboBox_day.currentIndex() == -1:
                myComboBox_hour.clear()
            elif myComboBox_hour.count() == 0:
                myComboBox_hour.addItems([''] + [str(x) for x in range(1, 25)])

        myComboBox_day = MyComboBox([], d)
        myComboBox_day.move(440, 180)
        myComboBox_day.currentIndexChanged.connect(on_day_change)

        myLabel_day = MyLabel('日', d)
        myLabel_day.move(540, 180)

        myComboBox_hour = MyComboBox([], d)
        myComboBox_hour.move(560, 180)

        myLabel_hour = MyLabel('时', d)
        myLabel_hour.move(660, 180)

        def maintain_data_slot():
            year = myComboBox_year.currentIndex() + 2000
            month = myComboBox_month.currentIndex()
            day = myComboBox_day.currentIndex()
            hour = myComboBox_hour.currentIndex()
            user_data = get_user_data_by_date_from_database(self.nowUserId, year, month, day, hour)
            if len(user_data) == 0:
                QtGui.QMessageBox.warning(d, "数据查询失败", "该日期没有数据", "确定")
                return
            d2 = MyDialog(d)
            user_data_id = user_data['id']
            user = get_user_by_id(self.nowUserId)

            myLabel_title = MyLabel(user['userType'] + '-' + user['userName'] + '用户：', d2)
            myLabel_title.move(100, 60)

            myLabel_gasCondition = MyLabel('用气工况：', d2)
            myLabel_gasCondition.move(100, 120)

            def on_newYear_change():
                if myComboBox_newMonth.currentIndex() == 2:
                    current_year = int(myComboBox_newYear.currentText())
                    myComboBox_newDay.clear()
                    if current_year % 400 == 0 or (current_year % 4 == 0 and current_year % 100 != 0):
                        myComboBox_newDay.addItems(day_dict['闰月'])
                    else:
                        myComboBox_newDay.addItems(day_dict['平月'])

            myComboBox_newYear = MyComboBox([str(x) for x in range(2000, 2051)], d2)
            myComboBox_newYear.move(200, 120)
            myComboBox_newYear.currentIndexChanged.connect(on_newYear_change)

            myLabel_newYear = MyLabel('年', d2)
            myLabel_newYear.move(300, 120)

            def on_newMonth_change():
                if myComboBox_newMonth.currentIndex() == 0:
                    myComboBox_newDay.clear()
                    myComboBox_hour.clear()
                    return
                current_month = myComboBox_newMonth.currentText()
                myComboBox_newDay.clear()
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

            myComboBox_newMonth = MyComboBox([''] + [str(x) for x in range(1, 13)], d2)
            myComboBox_newMonth.move(320, 120)
            myComboBox_newMonth.currentIndexChanged.connect(on_newMonth_change)

            myLabel_newMonth = MyLabel('月', d2)
            myLabel_newMonth.move(420, 120)

            def on_newDay_change():
                if myComboBox_newDay.currentIndex() == 0 or myComboBox_newDay.currentIndex() == -1:
                    myComboBox_newHour.clear()
                elif myComboBox_newHour.count() == 0:
                    myComboBox_newHour.addItems([''] + [str(x) for x in range(1, 25)])

            myComboBox_newDay = MyComboBox([], d2)
            myComboBox_newDay.move(440, 120)
            myComboBox_newDay.currentIndexChanged.connect(on_newDay_change)

            myLabel_newDay = MyLabel('日', d2)
            myLabel_newDay.move(540, 120)
            myComboBox_newHour = MyComboBox([], d2)
            myComboBox_newHour.move(560, 120)

            myComboBox_newYear.setCurrentIndex(year - 2000)
            myComboBox_newMonth.setCurrentIndex(month)
            myComboBox_newDay.setCurrentIndex(day)
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
            d2.connect(myButton_cancel, QtCore.SIGNAL("clicked()"), delete_user_data)

            def update_user_data():
                gasNum = myLineEdit_gasNum.text()
                userNum = myLineEdit_userNum.text()
                newYear = int(myComboBox_newYear.currentText())
                newMonth = myComboBox_newMonth.currentIndex()
                newDay = myComboBox_newDay.currentIndex()
                newHour = myComboBox_newHour.currentIndex()
                if gasNum == '':
                    QtGui.QMessageBox.warning(d2, "数据修改失败", "用气量不能为空！", "确定")
                    return
                if userNum == '':
                    QtGui.QMessageBox.warning(d2, "数据修改失败", "用户数不能为空！", "确定")
                    return
                try:
                    gasNum = float(gasNum)
                    userNum = int(userNum)
                    update_user_data_from_database(user_data_id, gasNum, userNum, newYear, newMonth, newDay, newHour)
                    QtGui.QMessageBox.information(d2, "数据修改成功", "修改成功！", "确定")
                    d2.close()
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

        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
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

    def search_gas_index_fuc(self):
        search_gas_index_component_dict = {}

        myLabel_indexType = MyLabel('指标类型：', self)
        myLabel_indexType.move(100, 60)
        search_gas_index_component_dict['myLabel_indexType'] = myLabel_indexType

        myComboBox_indexType = MyComboBox(['年', '月'], self)
        myComboBox_indexType.move(200, 60)
        search_gas_index_component_dict['myComboBox_indexType'] = myComboBox_indexType

        myLabel_userType = MyLabel('用户类型：', self)
        myLabel_userType.move(100, 120)
        search_gas_index_component_dict['myLabel_userType'] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 120)
        search_gas_index_component_dict['myComboBox_userType'] = myComboBox_userType

        myLabel_userName = MyLabel('用户名称：', self)
        myLabel_userName.move(100, 180)
        search_gas_index_component_dict['myLabel_userName'] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 180)
        search_gas_index_component_dict['myComboBOx_userName'] = myComboBox_userName

        myLabel_date = MyLabel('日期：', self)
        myLabel_date.move(100, 240)
        search_gas_index_component_dict['myLabel_date'] = myLabel_date

        myComboBox_year = MyComboBox([str(x) for x in range(2000, 2101)], self)
        myComboBox_year.move(200, 240)
        search_gas_index_component_dict['myComboBox_year'] = myComboBox_year

        myLabel_year = MyLabel('年', self)
        myLabel_year.move(300, 240)
        search_gas_index_component_dict['myLabel_year'] = myLabel_year

        myComboBox_month = MyComboBox([str(x) for x in range(1, 13)], self)
        myComboBox_month.move(320, 240)
        search_gas_index_component_dict['myComboBox_month'] = myComboBox_month

        myLabel_month = MyLabel('月', self)
        myLabel_month.move(420, 240)
        search_gas_index_component_dict['myLabel_month'] = myLabel_month

        myButton_search = MyButton('查询', self)
        myButton_search.move(100, 300)
        search_gas_index_component_dict['myButton_search'] = myButton_search

        myLabel_indexTitle = MyLabel('用气指标：', self)
        myLabel_indexTitle.move(500, 150)
        search_gas_index_component_dict['myLabel_indexTitle'] = myLabel_indexTitle

        myLabel_index = MyLabel('', self)
        myLabel_index.resize(500, 30)
        myLabel_index.move(600, 150)
        search_gas_index_component_dict['myLabel_index'] = myLabel_index

        def on_indexType_change():
            if myComboBox_indexType.currentText() == '年':
                myComboBox_month.hide()
                myLabel_month.hide()
            else:
                myComboBox_month.show()
                myLabel_month.show()

        def search_gas_index():
            index_type = myComboBox_indexType.currentText()
            user_id = self.nowUserId
            user_content = get_user_by_id(user_id)
            year = int(myComboBox_year.currentText())
            month = int(myComboBox_month.currentText())
            gas_index = get_gas_index_from_database(user_id, index_type, year, month)
            if gas_index is None:
                gas_index = 0
            if gas_index == -1:
                QtGui.QMessageBox.warning(self, '查询失败', '该用户没有用气数据', '确认')
                return
            if gas_index == -2:
                QtGui.QMessageBox.warning(self, '查询失败', '该用户没有月用气数据', '确认')
                return
            myLabel_index.setText(('%.6f' % gas_index) + ' ' + user_content['gasUnit'] + '/' + user_content['userUnit']
                                  + '·' + myComboBox_indexType.currentText())

        myComboBox_indexType.currentIndexChanged.connect(on_indexType_change)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        self.connect(myButton_search, QtCore.SIGNAL('clicked()'), search_gas_index)
        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        self.all_component['search_gas_index'] = search_gas_index_component_dict

        for i in search_gas_index_component_dict.values():
            i.hide()

    def display_search_gas_index(self):
        for i in self.all_component.values():
            for j in i.values():
                j.hide()
        for i in self.all_component['search_gas_index'].values():
            i.show()

        user_type = get_all_userType()
        self.all_component['search_gas_index']['myComboBox_userType'].clear()
        self.all_component['search_gas_index']['myComboBox_userType'].addItems(user_type)
        if self.all_component['search_gas_index']['myComboBox_indexType'].currentText() == '年':
            self.all_component['search_gas_index']['myComboBox_month'].hide()
            self.all_component['search_gas_index']['myLabel_month'].hide()
        return

    def examine_index_result_fuc(self):
        examine_index_result_component_dict = {}

        myLabel_indexType = MyLabel('指标类型：', self)
        myLabel_indexType.move(100, 60)
        examine_index_result_component_dict['myLabel_indexType'] = myLabel_indexType

        myComboBox_indexType = MyComboBox(['年', '月'], self)
        myComboBox_indexType.move(200, 60)
        examine_index_result_component_dict['myComboBox_indexType'] = myComboBox_indexType

        myLabel_userType = MyLabel('用户类型：', self)
        myLabel_userType.move(100, 120)
        examine_index_result_component_dict['myLabel_userType'] = myLabel_userType

        myComboBox_userType = MyComboBox([], self)
        myComboBox_userType.move(200, 120)
        examine_index_result_component_dict['myComboBox_userType'] = myComboBox_userType

        myLabel_userName = MyLabel('用户名称：', self)
        myLabel_userName.move(100, 180)
        examine_index_result_component_dict['myLabel_userName'] = myLabel_userName

        myComboBox_userName = MyComboBox([], self)
        myComboBox_userName.move(200, 180)
        examine_index_result_component_dict['myComboBOx_userName'] = myComboBox_userName

        myLabel_startDate = MyLabel('开始日期：', self)
        myLabel_startDate.move(100, 240)
        examine_index_result_component_dict['myLabel_startDate'] = myLabel_startDate

        myComboBox_startYear = MyComboBox([str(x) for x in range(2000, 2101)], self)
        myComboBox_startYear.move(200, 240)
        examine_index_result_component_dict['myComboBox_startYear'] = myComboBox_startYear

        myLabel_startYear = MyLabel('年', self)
        myLabel_startYear.move(300, 240)
        examine_index_result_component_dict['myLabel_startYear'] = myLabel_startYear

        myComboBox_startMonth = MyComboBox([str(x) for x in range(1, 13)], self)
        myComboBox_startMonth.move(320, 240)
        examine_index_result_component_dict['myComboBox_startMonth'] = myComboBox_startMonth

        myLabel_startMonth = MyLabel('月', self)
        myLabel_startMonth.move(420, 240)
        examine_index_result_component_dict['myLabel_startMonth'] = myLabel_startMonth

        myLabel_endDate = MyLabel('结束日期：', self)
        myLabel_endDate.move(100, 300)
        examine_index_result_component_dict['myLabel_endDate'] = myLabel_endDate

        myComboBox_endYear = MyComboBox([str(x) for x in range(2000, 2101)], self)
        myComboBox_endYear.move(200, 300)
        examine_index_result_component_dict['myComboBox_endYear'] = myComboBox_endYear

        myLabel_endYear = MyLabel('年', self)
        myLabel_endYear.move(300, 300)
        examine_index_result_component_dict['myLabel_endYear'] = myLabel_endYear

        myComboBox_endMonth = MyComboBox([str(x) for x in range(1, 13)], self)
        myComboBox_endMonth.move(320, 300)
        examine_index_result_component_dict['myComboBox_endMonth'] = myComboBox_endMonth

        myLabel_endMonth = MyLabel('月', self)
        myLabel_endMonth.move(420, 300)
        examine_index_result_component_dict['myLabel_endMonth'] = myLabel_endMonth

        myButton_examine = MyButton('确认', self)
        myButton_examine.move(100, 360)
        examine_index_result_component_dict['myButton_examine'] = myButton_examine

        def on_indexType_change():
            if myComboBox_indexType.currentText() == '年':
                myComboBox_startMonth.hide()
                myLabel_startMonth.hide()
                myComboBox_endMonth.hide()
                myLabel_endMonth.hide()
            else:
                myComboBox_startMonth.show()
                myLabel_startMonth.show()
                myComboBox_endMonth.show()
                myLabel_endMonth.show()

        def on_button_click():
            start_month = int(myComboBox_startMonth.currentText())
            start_year = int(myComboBox_startYear.currentText())
            end_month = int(myComboBox_endMonth.currentText())
            end_year = int(myComboBox_endYear.currentText())
            if (start_year, start_month) > (end_year, end_month):
                QtGui.QMessageBox.warning(self, '查看失败', '开始时间不能晚于结束时间', '确定')
                return
            index_list = get_index_of_user_in_times_from_database(self.nowUserId, myComboBox_indexType.currentText(),
                                                                  start_year, start_month, end_year, end_month)
            weather_list = get_weather_in_times_from_database(myComboBox_indexType.currentText(), start_year,
                                                              start_month, 0, end_year, end_month, 0)
            # print(index_list, weather_list)
            self.examine_index_result_slot(index_list, weather_list)

        myComboBox_indexType.currentIndexChanged.connect(on_indexType_change)
        myComboBox_userType.currentIndexChanged.connect(self.selectionchange)
        myComboBox_userName.currentIndexChanged.connect(self.selectUser)
        self.connect(myButton_examine, QtCore.SIGNAL('clicked()'), on_button_click)
        self.comboBoxPair[myComboBox_userType] = myComboBox_userName

        self.all_component['examine_index_result'] = examine_index_result_component_dict

        for i in examine_index_result_component_dict.values():
            i.hide()

    def examine_index_result_slot(self, index_list, weather_list):
        d = MyDialog(self)
        user_content = get_user_by_id(self.nowUserId)
        unit = user_content['gasUnit'] + '/' + user_content['userUnit'] + '·' + \
               self.all_component['examine_index_result']['myComboBox_indexType'].currentText()
        temp_index_list = deepcopy(index_list)
        for row in temp_index_list:
            row[1] = str(row[1]) + ' ' + unit
        myTable_index = MyTable(d, temp_index_list, ['日期', '用气指标'])
        myTable_index.move(0, 0)

        flag = True
        for w in weather_list:
            if len(w) <= 3:
                flag = False
        if not flag:
            weather_list = []

        myPlot_index = MyPlot(d, index_list, unit, weather_list, '指标折线图')
        myPlot_index.move(250, 0)
        d.setWindowTitle("结果查看")
        d.setWindowModality(QtCore.Qt.ApplicationModal)
        d.exec_()

    def display_examine_index_result(self):
        for i in self.all_component.values():
            for j in i.values():
                j.hide()
        for i in self.all_component['examine_index_result'].values():
            i.show()

        user_type = get_all_userType()
        self.all_component['examine_index_result']['myComboBox_userType'].clear()
        self.all_component['examine_index_result']['myComboBox_userType'].addItems(user_type)
        if self.all_component['examine_index_result']['myComboBox_indexType'].currentText() == '年':
            self.all_component['examine_index_result']['myComboBox_startMonth'].hide()
            self.all_component['examine_index_result']['myLabel_startMonth'].hide()
            self.all_component['examine_index_result']['myComboBox_endMonth'].hide()
            self.all_component['examine_index_result']['myLabel_endMonth'].hide()

