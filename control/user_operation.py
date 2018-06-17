from database.sqlquery import insert_user


def add_user(userType, userName, gasUnit, userUnit, remark=''):
    return insert_user(userType, userName, gasUnit, userUnit, remark)
