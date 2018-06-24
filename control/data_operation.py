from database.sqlquery import insert_weather, insert_user_data, check_admin, get_user_date, get_user_data_by_date, \
    update_user_data, delete_user_data
from database.sqlquery import insert_weather, insert_user_data
from database.sqlquery import get_all_user_gasIndex
import time


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
        ws = wb.add_sheet('所有用户的年用气指标')
        ws.write(0, 0, "用户类型")
        ws.write(0, 1, "用户名称")
        ws.write(0, 2, "用气指标")
        ws.write(0, 3, "指标单位")

        for i, row in enumerate(data_list):
            for j, content in enumerate(row):
                ws.write(i + 1, j, content)

        wb.save(file_p)

    res = [True, ""]
    try:
        gasIndex_list = get_all_user_gasIndex(timeType, start_time, stop_time)
        export_to_file(gasIndex_list, file_path)
    except Exception as e:
        res[0] = False
        res[1] = str(e)
    return res
