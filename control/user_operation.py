from database.sqlquery import get_user as gu
from database.sqlquery import insert_user as iu
from database.sqlquery import update_user as uu
from database.sqlquery import delete_user as du
from database.sqlquery import get_all_userType as gau
from database.sqlquery import get_userNames_by_userType as gubu
from database.sqlquery import get_user_by_id as gubi
from database.sqlquery import insert_weather
import time

def add_user(userType, userName, gasUnit, userUnit, remark=''):
    exist = gu(userType, userName)
    # print(exist)
    if exist:
        return [False, "该用户已存在"]
    else:
        return iu(userType, userName, gasUnit, userUnit, remark)


def get_all_userType():
    return gau()


def get_userNames_by_userType(userType):
    return gubu(userType)


def get_user_by_id(id):
    return gubi(id)

def get_user(userType, userName):
    return gu(userType, userName)

def add_weather(date, maxTemperature, minTemperature, avgTemperature):
    insert_weather(date, maxTemperature, minTemperature, avgTemperature)


def update_user(id, userType, userName, gasUnit, userUnit):
    return uu(id, userType, userName, gasUnit, userUnit)


def delete_user(id):
    return du(id)

def datetime_to_timestamp(datetime, format):
    """
    日期时间转化为时间戳
    :param datetime: 日期时间
    :param format: 格式，年：%y，月：%m，日：%d，时：%H，分：%M，秒：%S, 如'%Y-%m-%d %H:%M:%S'
    :return:
    """
    return int(time.mktime(time.strptime(datetime, format)))
