from database.sqlquery import insert_user, insert_weather
import time

def add_user(userType, userName, gasUnit, userUnit, remark=''):
    return insert_user(userType, userName, gasUnit, userUnit, remark)


def add_weather(date, maxTemperature, minTemperature, avgTemperature):
    insert_weather(date, maxTemperature, minTemperature, avgTemperature)


def datetime_to_timestamp(datetime, format):
    """
    日期时间转化为时间戳
    :param datetime: 日期时间
    :param format: 格式，年：%y，月：%m，日：%d，时：%H，分：%M，秒：%S, 如'%Y-%m-%d %H:%M:%S'
    :return:
    """
    return int(time.mktime(time.strptime(datetime, format)))
