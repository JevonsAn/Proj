from database.sqlquery import check_admin, get_user_date, get_user_data_by_date, update_user_data, delete_user_data
from database.sqlquery import insert_weather, insert_user_data
from database.sqlquery import get_all_user_info, get_many_avg_gas
from control.gas_index_opeartion import get_gas_index_from_database
from control.user_operation import get_user_by_id
from control.uneven_operation import search_uneven
import time
import datetime


def add_weather(date, maxTemperature, minTemperature, avgTemperature):
    insert_weather(date, maxTemperature, minTemperature, avgTemperature)


def datetime_to_timestamp(datetime, format):
    """
    日期时间转化为时间戳
    :param datetime: 日期时间
    :param format: 格式，年：%Y，月：%m，日：%d，时：%H，分：%M，秒：%S, 如'%Y-%m-%d %H:%M:%S'
    :return:
    """
    return int(time.mktime(time.strptime(datetime, format)))

def add_user_data(userId, gasNum, userNum, year, month, day, hour):
    insert_user_data(userId, gasNum, userNum, year, month, day, hour)


def check_admin_password(username, password):
    return check_admin(username, password)


def get_user_date_from_database(user_id):
    return get_user_date(user_id)


def get_user_data_by_date_from_database(user_id, year, month, day, hour):
    return get_user_data_by_date(user_id, year, month, day, hour)


def update_user_data_from_database(user_data_id, gas_num, user_num, year, month, day, hour):
    update_user_data(user_data_id, gas_num, user_num, year, month, day, hour)


def delete_user_data_from_database(user_data_id):
    delete_user_data(user_data_id)

def export_gasIndex(timeType, start_time, stop_time, file_path):
    def export_to_file(data_list, file_p):
        import xlwt
        wb = xlwt.Workbook()
        ws = wb.add_sheet('所有用户的用气指标')

        font0 = xlwt.Font()
        font0.bold = True
        align = xlwt.Alignment()
        align.horz = xlwt.Alignment().HORZ_CENTER
        align.vert = xlwt.Alignment().VERT_CENTER

        bold_style = xlwt.XFStyle()
        bold_style.font = font0
        bold_style.alignment = align

        general_style = xlwt.XFStyle()
        general_style.alignment = align

        ws.write(0, 0, "用户类型", bold_style)
        ws.write(0, 1, "用户名称", bold_style)
        ws.write(0, 2, "时间", bold_style)
        ws.write(0, 3, "用气指标", bold_style)
        ws.write(0, 4, "指标单位", bold_style)

        for i, row in enumerate(data_list):
            for j, content in enumerate(row):
                ws.write(i + 1, j, content, general_style)

        wb.save(file_p)

    def timeChange(timeType, t):
        if timeType == "月":
            return "%d年%d月" % (t[0], t[1])
        elif timeType == "年":
            return "%d年" % t[0]

    res = [True, ""]
    try:
        user_list = get_all_user_info()
        gasIndex_list = []

        all_time = {timeType: []}
        if timeType == "年":
            all_time[timeType] = [(x, 0) for x in range(int(start_time), int(stop_time) + 1)]
        elif timeType == "月":
            all_time[timeType] = [(int(start_time[:4]), m) for m in range(int(start_time[4:]), 13)] \
                                 + [(x, m) for x in range(int(start_time[:4]) + 1, int(stop_time[:4])) for m in
                                    range(1, 13)] \
                                 + [(int(stop_time[:4]), m) for m in range(1, int(stop_time[4:]) + 1)]

        for user in user_list:
            for t in all_time[timeType]:
                lt = []
                lt.append(user["userType"])
                lt.append(user["userName"])
                lt.append(timeChange(timeType, t))
                gasIndex = get_gas_index_from_database(user["id"], timeType, *t)
                if gasIndex == 0 or abs(gasIndex) <= 0.00001:
                    continue
                lt.append(gasIndex)
                lt.append(user["unit"] + " · %s" % timeType)
                gasIndex_list.append(lt)

        export_to_file(gasIndex_list, file_path)
    except PermissionError as e:
        res[0] = False
        res[1] = str("没有写入文件的权限，可能是文件未关闭导致")
    except Exception as e:
        raise e
        res[0] = False
        print(e)
        res[1] = str(e)
    return res


def export_uneven(user_id, timeType, start_time, stop_time, file_path):
    def export_to_file(data_list, file_p):
        import xlwt
        wb = xlwt.Workbook()
        ws = wb.add_sheet('sheet1')

        font0 = xlwt.Font()
        font0.bold = True
        align = xlwt.Alignment()
        align.horz = xlwt.Alignment().HORZ_CENTER
        align.vert = xlwt.Alignment().VERT_CENTER

        bold_style = xlwt.XFStyle()
        bold_style.font = font0
        bold_style.alignment = align

        general_style = xlwt.XFStyle()
        general_style.alignment = align

        # ws.write(0, 0, "用户类型", bold_style)
        # ws.write(0, 1, "用户名称", bold_style)
        ws.write(0, 0, "时间", bold_style)
        ws.write(0, 1, "不均匀系数", bold_style)

        for i, row in enumerate(data_list):
            for j, content in enumerate(row):
                ws.write(i + 1, j, content, general_style)

        wb.save(file_p)

    def timeChange(timeType, t):
        if timeType == "月":
            year = int(t[:4])
            month = int(t[4:6])
            return "%d-%d" % (year, month)
        elif timeType == "小时":
            year = int(t[:4])
            month = int(t[4:6])
            day = int(t[6:8])
            hour = int(t[8:10])
            return "%d-%d-%d : %d时" % (year, month, day, hour)
        elif timeType == "周":
            year = int(t[:4])
            month = int(t[4:6])
            day = int(t[6:8])
            return "%d-%d-%d" % (year, month, day)
        elif timeType == "日":
            year = int(t[:4])
            month = int(t[4:6])
            day = int(t[6:8])
            return "%d-%d-%d" % (year, month, day)

    res = [True, ""]
    try:
        time_gas = get_many_avg_gas(user_id, timeType, start_time, stop_time)

        all_time = {}
        if timeType == "月":
            all_time[timeType] = ["%4d%2d" % (int(start_time[:4]), m) for m in range(int(start_time[4:6]), 13)] \
                                 + ["%4d%2d" % (x, m) for x in range(int(start_time[:4]) + 1, int(stop_time[:4])) for m
                                    in range(1, 13)] \
                                 + ["%4d%2d" % (int(stop_time[:4]), m) for m in range(1, int(stop_time[4:6]) + 1)]
        elif timeType == "日":
            dayfrom = datetime.datetime.strptime(start_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayto = datetime.datetime.strptime(stop_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayscount = (dayto - dayfrom).days
            all_time[timeType] = []
            for i in range(dayscount):
                d = dayfrom + datetime.timedelta(days=i)
                all_time[timeType].append("%4d%2d%2d" % (d.year, d.month, d.day))

        elif timeType == "周":
            dayfrom = datetime.datetime.strptime(start_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayto = datetime.datetime.strptime(stop_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayscount = (dayto - dayfrom).days
            all_time[timeType] = []
            for i in range(dayscount):
                d = dayfrom + datetime.timedelta(days=i)
                all_time[timeType].append("%4d%2d%2d" % (d.year, d.month, d.day))

        elif timeType == "小时":
            dayfrom = datetime.datetime.strptime(start_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayto = datetime.datetime.strptime(stop_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayscount = (dayto - dayfrom).days
            all_time[timeType] = []
            for i in range(dayscount):
                d = dayfrom + datetime.timedelta(days=i)
                for h in range(1, 23):
                    all_time[timeType].append("%4d%2d%2d%2d" % (d.year, d.month, d.day, h))

        gasIndex_list = []

        for t in all_time[timeType]:
            lt = []
            # lt.append(user["userType"])
            # lt.append(user["userName"])
            lt.append(timeChange(timeType, t))
            lres = search_uneven(user_id, timeType, t, time_gas)
            if lres[0] is False or lres[1] == 0:
                continue
            else:
                lt.append(lres[1])
            gasIndex_list.append(lt)

        export_to_file(gasIndex_list, file_path)
    except PermissionError as e:
        res[0] = False
        res[1] = str("没有写入文件的权限，可能是文件未关闭导致")
    except Exception as e:
        raise e
        # res[0] = False
        # print(e)
        # res[1] = str(e)
    return res
