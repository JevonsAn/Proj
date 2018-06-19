from database.sqlquery import insert_user

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


def update_user(id, userType, userName, gasUnit, userUnit):
    return uu(id, userType, userName, gasUnit, userUnit)


def delete_user(id):
    return du(id)

