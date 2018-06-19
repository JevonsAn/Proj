from database.sqlconnection import Mysql
from pymysql import IntegrityError


def get_user(userType, userName):
    mysqlserver = Mysql()
    sql = "SELECT gasUnit, userUnit FROM data.user where userType=%s and userName=%s;"
    mysqlserver.exe(sql, (userType, userName))
    user = {}
    for row in mysqlserver.results():
        user['gasUnit'] = row[0]
        user['userUnit'] = row[1]
        user["userType"] = userType
        user["userName"] = userName
    mysqlserver.closeSQL()
    return user


def get_all_userType():
    mysqlserver = Mysql()
    sql = "SELECT distinct userType FROM data.user;"
    mysqlserver.exe(sql)
    userTypes = []
    for row in mysqlserver.results():
        userTypes.append(row[0])
    mysqlserver.closeSQL()
    return userTypes


def get_all_user_gasIndex(timeType, start_time, stop_time):
    mysqlserver = Mysql()
    timeType2Int = {"年": 1, "月": 2, "日": 3, "小时": 4}
    year_sql = "select u.userType, u.userName, sum(d.gasNum / d.userNum), u.gasUnit, u.userUnit from user u, userdata d " \
               "where u.id = d.user_id and u.timeType >= %s and d.year >= %s and d.year <= %s group by d.user_id;"
    month_sql = "select u.userType, u.userName, sum(d.gasNum / d.userNum), u.gasUnit, u.userUnit from user u, userdata d " \
                "where u.id = d.user_id and u.timeType >= %s and (d.year, d.month) >= (%s, %s) and (d.year, d.month) <= (%s, %s) group by d.user_id;"
    if timeType == "年":
        sql = year_sql
        params = (timeType2Int[timeType], int(start_time), int(stop_time))
    elif timeType == "月":
        sql = month_sql
        params = (
        timeType2Int[timeType], int(start_time[:5]), int(start_time[5:]), int(stop_time[:5]), int(stop_time[5:]))
    else:
        raise ValueError("不应该的时间指标类型")

    print(sql % params)
    mysqlserver.exe(sql, params)

    gasIndex = []
    for row in mysqlserver.results():
        index = []
        # index["useType"] = row[0]
        # index["useName"] = row[1]
        # index["gasIndex"] = row[2]
        # index["unit"] = "%s / %s · %s" % (row[3], row[4], timeType)
        index.append(row[0])
        index.append(row[1])
        index.append(row[2])
        index.append("%s / %s · %s" % (row[3], row[4], timeType))
        gasIndex.append(index)
    mysqlserver.closeSQL()
    return gasIndex


def get_userNames_by_userType(userType):
    mysqlserver = Mysql()
    sql = "SELECT userName, id FROM data.user WHERE userType=%s;"
    mysqlserver.exe(sql, (userType,))
    userNames = []
    userName2id = {}
    for row in mysqlserver.results():
        userNames.append(row[0])
        userName2id[row[0]] = row[1]
    mysqlserver.closeSQL()
    return userNames, userName2id


def get_user_by_id(id):
    mysqlserver = Mysql()
    sql = "SELECT userType, userName, gasUnit, userUnit, timeType FROM data.user WHERE id=%s;"
    mysqlserver.exe(sql, (id,))
    user = {}
    for row in mysqlserver.results():
        user["userType"] = row[0]
        user["userName"] = row[1]
        user["gasUnit"] = row[2]
        user["userUnit"] = row[3]
        user["timeType"] = int(row[4])
    mysqlserver.closeSQL()
    return user


def update_user(id, userType, userName, gasUnit, userUnit):
    mysqlserver = Mysql()
    sql = "UPDATE `data`.`user` t SET t.`userType` = %s, t.`userName` = %s, t.`gasUnit` = %s, t.`userUnit` = %s WHERE t.`id` = %s"
    res = [True, '']
    try:
        mysqlserver.exe(sql, (userType, userName, gasUnit, userUnit, id,))
        mysqlserver.commit()
    except Exception as e:
        res = [False, "数据库错误" + str(e)]
    finally:
        mysqlserver.closeSQL()
        return res


def insert_user(userType, userName, gasUnit, userUnit, remark=''):
    mysqlserver = Mysql()
    # mysqlserver.openSQL()
    sql = "INSERT INTO `data`.`user` (`userType`, `userName`, `gasUnit`, `userUnit`) VALUES (%s, %s, %s, %s);"
    res = [True, '']
    try:
        mysqlserver.exe(sql, (userType, userName, gasUnit, userUnit))
        mysqlserver.commit()
    except Exception as e:
        res = [False, "数据库错误" + str(e)]
    finally:
        mysqlserver.closeSQL()
        return res


def delete_user(id):
    mysqlserver = Mysql()
    sql = "DELETE FROM `data`.`user` WHERE `id` = %s"
    res = [True, '']
    try:
        mysqlserver.exe(sql, (int(id),))
        mysqlserver.commit()
    except Exception as e:
        res = [False, "数据库错误" + str(e)]
    finally:
        mysqlserver.closeSQL()
        return res


def insert_weather(date, maxTemperature, minTemperature, avgTemperature):
    mysqlserver = Mysql()
    sql = 'INSERT INTO data.weather (date, max, min, ord) VALUES (%s, %s, %s, %s);'
    mysqlserver.exe(sql, (date, maxTemperature, minTemperature, avgTemperature))
    mysqlserver.commit()
    mysqlserver.closeSQL()


def insert_user_data(userId, timeType, gasNum, userNum, year, month, day, hour):
    mysqlserver = Mysql()
    newTimeType = timeType
    if timeType == 5:
        if year:
            newTimeType = 1
        if month:
            newTimeType = 2
        if day:
            newTimeType = 3
        if hour:
            newTimeType = 4
    if newTimeType == 1:
        sql = 'INSERT INTO data.userdata (user_id, gasNum, userNum, year) VALUES (%s, %s, %s, %s);'
        mysqlserver.exe(sql, (userId, gasNum, userNum, year))
    elif newTimeType == 2:
        sql = 'INSERT INTO data.userdata (user_id, gasNum, userNum, year, month) VALUES (%s, %s, %s, %s, %s);'
        mysqlserver.exe(sql, (userId, gasNum, userNum, year, month))
    elif newTimeType == 3:
        sql = 'INSERT INTO data.userdata (user_id, gasNum, userNum, year, month, day) VALUES (%s, %s, %s, %s, %s, %s);'
        mysqlserver.exe(sql, (userId, gasNum, userNum, year, month, day))
    else:
        sql = 'INSERT INTO data.userdata (user_id, gasNum, userNum, year, month, day, hour) ' \
              'VALUES (%s, %s, %s, %s, %s, %s, %s);'
        mysqlserver.exe(sql, (userId, gasNum, userNum, year, month, day, hour))
    if timeType == 5:
        sql = 'UPDATE user SET timeType = %s WHERE id = %s'
        mysqlserver.exe(sql, (newTimeType, userId))
    mysqlserver.commit()
    mysqlserver.closeSQL()
