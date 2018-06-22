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
    # 加一列当前时间
    year_sql = "select u.userType, u.userName, sum(d.gasNum / d.userNum), u.gasUnit, u.userUnit from user u, userdata d " \
               "where u.id = d.user_id and u.timeType >= %s and d.year >= %s and d.year <= %s group by d.user_id, d.year;"
    month_sql = "select u.userType, u.userName, sum(d.gasNum / d.userNum), u.gasUnit, u.userUnit from user u, userdata d " \
                "where u.id = d.user_id and u.timeType >= %s and (d.year, d.month) >= (%s, %s) and (d.year, d.month) <= (%s, %s) group by d.user_id, d.month, d.year;"
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


def check_admin(username, password):
    mysql_server = Mysql()
    sql = 'SELECT count(*) FROM administrator WHERE administrator.name = %s and administrator.password = %s'
    mysql_server.exe(sql, (username, password))
    for row in mysql_server.results():
        if row[0] == 1:
            return True
        return False
    mysql_server.closeSQL()


def get_user_date(user_id):
    date_dict = {}
    mysql_server = Mysql()
    sql = 'SELECT year, month, day, hour FROM userdata WHERE user_id = %s'
    mysql_server.exe(sql, (user_id,))
    for row in mysql_server.results():
        year = row[0]
        month = row[1]
        day = row[2]
        hour = row[3]
        if year not in date_dict.keys():
            date_dict[year] = {}
        if month not in date_dict[year].keys():
            date_dict[year][month] = {}
        if day not in date_dict[year][month].keys():
            date_dict[year][month][day] = set()
        if hour not in date_dict[year][month][day]:
            date_dict[year][month][day].add(hour)
    mysql_server.closeSQL()
    return date_dict


def get_user_data_by_date(user_id, year, month, day, hour):
    user_data = {}
    mysql_server = Mysql()
    sql = 'SELECT id, gasNum, userNum FROM userdata WHERE user_id = %s and year = %s and month = %s and day = %s and ' \
          'hour = %s'
    mysql_server.exe(sql, (user_id, year, month, day, hour))
    for row in mysql_server.results():
        user_data['id'] = row[0]
        user_data['gasNum'] = row[1]
        user_data['userNum'] = row[2]
    mysql_server.closeSQL()
    return user_data


def update_user_data(user_data_id, gas_num, user_num, year, month, day, hour):
    mysql_server = Mysql()
    sql = 'UPDATE userdata SET gasNum = %s, userNum = %s, year = %s, month = %s, day = %s, hour = %s ' \
          'WHERE userdata.id = %s'
    mysql_server.exe(sql, (gas_num, user_num, year, month, day, hour, user_data_id))
    mysql_server.commit()
    mysql_server.closeSQL()


def delete_user_data(user_data_id):
    mysql_server = Mysql()
    sql = 'DELETE FROM userdata WHERE id = %s'
    mysql_server.exe(sql, (user_data_id, ))
    mysql_server.commit()
    mysql_server.closeSQL()