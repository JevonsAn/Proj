import datetime
from database.sqlconnection import Mysql
from pymysql import IntegrityError

month_dict = {'大月': ['1', '3', '5', '7', '8', '10', '12'], '小月': ['4', '6', '9', '11']}
day_dict = {'小月': [str(x) for x in range(1, 31)], '大月': [str(x) for x in range(1, 32)],
            '平月': [str(x) for x in range(1, 29)], '闰月': [str(x) for x in range(1, 30)]}


def get_gas_by_alltime(index_type, time_gas, time):
    if index_type == "年":
        year = int(time[:4])
        all = 0
        if year in time_gas:
            mts = time_gas[year]
            mts_keys = mts.keys()
            if 0 in mts_keys:
                all = mts[0][0][0]
            else:
                for m in mts_keys:
                    days = mts[m]
                    days_keys = days.keys()
                    if 0 in days_keys:
                        all += days[0][0]
                    else:
                        for d in days_keys:
                            hours = days[d]
                            hours_keys = hours.keys()
                            if 0 in hours_keys:
                                all += hours[0]
                            else:
                                for h in hours_keys:
                                    all += hours[h]
        else:
            pass
        return all
    elif index_type == "月":
        year = int(time[:4])
        month = int(time[4:6])
        all = 0
        if year in time_gas:
            if month in time_gas[year]:
                days = time_gas[year][month]
                days_keys = days.keys()
                if 0 in days_keys:
                    all += days[0][0]
                else:
                    for d in days_keys:
                        hours = days[d]
                        hours_keys = hours.keys()
                        if 0 in hours_keys:
                            all += hours[0]
                        else:
                            for h in hours_keys:
                                all += hours[h]
            else:
                pass
        else:
            pass
        return all
    elif index_type == "日":
        year = int(time[:4])
        month = int(time[4:6])
        day = int(time[6:8])
        all = 0
        if year in time_gas:
            if month in time_gas[year]:
                if day in time_gas[year][month]:
                    hours = time_gas[year][month][day]
                    hours_keys = hours.keys()
                    if 0 in hours_keys:
                        all += hours[0]
                    else:
                        for h in hours_keys:
                            all += hours[h]
        return all
    elif index_type == "小时":
        year = int(time[:4])
        month = int(time[4:6])
        day = int(time[6:8])
        hour = int(time[8:10])
        all = 0
        if year in time_gas:
            if month in time_gas[year]:
                if day in time_gas[year][month]:
                    if hour in time_gas[year][month][day]:
                        all += time_gas[year][month][day][hour]
        return all


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


def get_gas_index(user_id, index_type, year, month):
    mysql_server = Mysql()
    # sql = 'SELECT timeType FROM user WHERE id = %s'
    # mysql_server.exe(sql, (user_id, ))
    # for row in mysql_server.results():
    #     time_type = row[0]
    # if time_type == 5:
    #     return -1
    if index_type == '年':
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum, u.userNum FROM userdata u WHERE u.user_id = %s and u.year = %s'
        mysql_server.exe(sql, (user_id, year))
    else:
        # if time_type == 1:
        #     return -2
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum, u.userNum FROM userdata u WHERE user_id = %s and u.year = %s and u.month = %s'
        mysql_server.exe(sql, (user_id, year, month))

    results = {}
    for row in mysql_server.results():
        if row[0] in results:
            if row[1] in results[row[0]]:
                if row[2] in results[row[0]][row[1]]:
                    if row[3] in results[row[0]][row[1]][row[2]]:
                        pass
                    else:
                        results[row[0]][row[1]][row[2]][row[3]] = row[4] / row[5]
                else:
                    results[row[0]][row[1]][row[2]] = {row[3]:
                                                           row[4] / row[5]
                                                       }
            else:
                results[row[0]][row[1]] = {row[2]:
                                               {row[3]:
                                                    row[4] / row[5]
                                                }
                                           }
        else:
            results[row[0]] = {row[1]:
                                   {row[2]:
                                        {row[3]:
                                             row[4] / row[5]
                                         }
                                    }
                               }

    return results


def get_avg_gas(user_id, time_type, search_time, results=None):
    year = 2000
    month = 0
    day = 0
    hour = 0
    dayfrom = None
    dayto = None

    if time_type == "年":
        year = int(search_time[:4])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and u.year = %s'
        params = (user_id, year)
        # print(sql % (user_id, year))

    elif time_type == "月":
        year = int(search_time[:4])
        month = int(search_time[4:6])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and (u.year, u.month) = (%s, %s)'
        params = (user_id, year, month)

    elif time_type == "日":
        year = int(search_time[:4])
        month = int(search_time[4:6])
        day = int(search_time[6:8])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and (u.year, u.month, u.day) = (%s, %s, %s)'
        params = (user_id, year, month, day)

    elif time_type == "周":
        vdate = datetime.datetime.strptime(search_time.replace(" ", "0"), '%Y%m%d').date()
        dayscount = datetime.timedelta(days=vdate.isoweekday())
        dayfrom = vdate - dayscount + datetime.timedelta(days=1)
        dayto = vdate - dayscount + datetime.timedelta(days=7)
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and (u.year, u.month, u.day) >= (%s, %s, %s) and (u.year, u.month, u.day) <= (%s, %s, %s)'
        params = (user_id, dayfrom.year, dayfrom.month, dayfrom.day, dayto.year, dayto.month, dayto.day)

    elif time_type == "小时":
        year = int(search_time[:4])
        month = int(search_time[4:6])
        day = int(search_time[6:8])
        hour = int(search_time[8:10])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and (u.year, u.month, u.day, u.hour) = (%s, %s, %s, %s)'
        params = (user_id, year, month, day, hour)

    if not results:
        mysql_server = Mysql()
        mysql_server.exe(sql, params)
        results = {}
        for row in mysql_server.results():
            if row[0] in results:
                if row[1] in results[row[0]]:
                    if row[2] in results[row[0]][row[1]]:
                        if row[3] in results[row[0]][row[1]][row[2]]:
                            pass
                        else:
                            results[row[0]][row[1]][row[2]][row[3]] = row[4]
                    else:
                        results[row[0]][row[1]][row[2]] = {row[3]:
                                                               row[4]
                                                           }
                else:
                    results[row[0]][row[1]] = {row[2]:
                                                   {row[3]:
                                                        row[4]
                                                    }
                                               }
            else:
                results[row[0]] = {row[1]:
                                       {row[2]:
                                            {row[3]:
                                                 row[4]
                                             }
                                        }
                                   }

    time_gas = results
    if time_type == "年":
        all_gas = get_gas_by_alltime(time_type, time_gas, search_time)
        # print(all_gas)

        days = 365
        if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
            days += 1
        avg_gas = all_gas / days
        return avg_gas

    elif time_type == "月":
        all_gas = get_gas_by_alltime(time_type, time_gas, search_time)

        current_month = month
        current_year = year

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

        avg_gas = all_gas / len(day_list)
        return avg_gas

    elif time_type == "日":
        all_gas = get_gas_by_alltime(time_type, time_gas, search_time)
        avg_gas = all_gas / 24
        return avg_gas

    elif time_type == "周":
        day_list = []
        for d in range(7):
            day = dayfrom + datetime.timedelta(days=d)
            day_list.append("%4d%2d%2d" % (day.year, day.month, day.day))
        # print(day_list)

        all_gas = 0
        for d in day_list:
            all_gas += get_gas_by_alltime("日", time_gas, d)
        avg_gas = all_gas / 7
        return avg_gas

    elif time_type == "小时":
        return get_gas_by_alltime(time_type, time_gas, search_time)


def get_many_avg_gas(user_id, time_type, start_time, stop_time):
    mysql_server = Mysql()
    if time_type == "年":
        start_year = int(start_time[:4])
        stop_year = int(stop_time[:4])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.id = %s and u.year >= %s and u.year <= %s'
        mysql_server.exe(sql, (user_id, start_year, stop_year))

    elif time_type == "月":
        start_year = int(start_time[:4])
        stop_year = int(stop_time[:4])
        start_month = int(start_time[4:6])
        stop_month = int(stop_time[4:6])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.id = %s and (u.year, u.month) >= (%s, %s) and (u.year, u.month) <= (%s, %s)'
        mysql_server.exe(sql, (user_id, start_year, start_month, stop_year, stop_month))

    elif time_type == "日" or time_type == "周":
        start_year = int(start_time[:4])
        start_month = int(start_time[4:6])
        start_day = int(start_time[6:8])
        stop_year = int(stop_time[:4])
        stop_month = int(stop_time[4:6])
        stop_day = int(stop_time[6:8])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and (u.year, u.month, u.day) >= (%s, %s, %s) and (u.year, u.month, u.day) <= (%s, %s, %s)'
        mysql_server.exe(sql, (user_id, start_year, start_month, start_day, stop_year, stop_month, stop_day))

    elif time_type == "小时":
        start_year = int(start_time[:4])
        start_month = int(start_time[4:6])
        start_day = int(start_time[6:8])
        start_hour = int(start_time[8:10])
        stop_year = int(stop_time[:4])
        stop_month = int(stop_time[4:6])
        stop_day = int(stop_time[6:8])
        stop_hour = int(stop_time[8:10])
        sql = 'SELECT u.year, u.month, u.day, u.hour, u.gasNum From userdata u where u.user_id = %s and (u.year, u.month, u.day, u.hour) >= (%s, %s, %s, %s) and (u.year, u.month, u.day, u.hour) <= (%s, %s, %s, %s)'
        mysql_server.exe(sql, (
        user_id, start_year, start_month, start_day, start_hour, stop_year, stop_month, stop_day, stop_hour))
    else:
        return

    results = {}
    for row in mysql_server.results():
        if row[0] in results:
            if row[1] in results[row[0]]:
                if row[2] in results[row[0]][row[1]]:
                    if row[3] in results[row[0]][row[1]][row[2]]:
                        pass
                    else:
                        results[row[0]][row[1]][row[2]][row[3]] = row[4]
                else:
                    results[row[0]][row[1]][row[2]] = {row[3]:
                                                           row[4]
                                                       }
            else:
                results[row[0]][row[1]] = {row[2]:
                                               {row[3]:
                                                    row[4]
                                                }
                                           }
        else:
            results[row[0]] = {row[1]:
                                   {row[2]:
                                        {row[3]:
                                             row[4]
                                         }
                                    }
                               }

    return results


def get_all_user_info():
    mysqlserver = Mysql()
    # timeType2Int = {"年": 1, "月": 2, "日": 3, "小时": 4}
    # year_sql = "select u.userType, u.userName, sum(d.gasNum / d.userNum),d.year, u.gasUnit, u.userUnit from user u, userdata d " \
    #            "where u.id = d.user_id and u.timeType >= %s and d.year >= %s and d.year <= %s group by d.user_id, d.year;"
    # month_sql = "select u.userType, u.userName, sum(d.gasNum / d.userNum),(d.year *100 + d.month), u.gasUnit, u.userUnit from user u, userdata d " \
    #             "where u.id = d.user_id and u.timeType >= %s and (d.year, d.month) >= (%s, %s) and (d.year, d.month) <= (%s, %s) group by d.user_id, d.month, d.year;"
    # if timeType == "年":
    #     sql = year_sql
    #     params = (timeType2Int[timeType], int(start_time), int(stop_time))
    # elif timeType == "月":
    #     sql = month_sql
    #     params = (timeType2Int[timeType], int(start_time[:5]), int(start_time[5:]), int(stop_time[:5]), int(stop_time[5:]))
    # else:
    #     raise ValueError("不应该的时间指标类型")

    sql = "SELECT id, userType, userName, gasUnit, userUnit FROM data.user;"

    mysqlserver.exe(sql)

    info = []
    for row in mysqlserver.results():
        index = {}
        index["id"] = row[0]
        index["userType"] = row[1]
        index["userName"] = row[2]
        index["unit"] = "%s / %s" % (row[3], row[4])

        info.append(index)
    mysqlserver.closeSQL()
    return info


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
    sql0 = 'delete from userdata where user_id = %s'
    sql = "DELETE FROM `data`.`user` WHERE `id` = %s"
    res = [True, '']
    try:
        mysqlserver.exe(sql0, (int(id),))
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


def insert_user_data(userId, gasNum, userNum, year, month, day, hour):
    mysqlserver = Mysql()
    sql = 'INSERT INTO data.userdata (user_id, gasNum, userNum, year, month, day, hour) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s);'
    mysqlserver.exe(sql, (userId, gasNum, userNum, year, month, day, hour))
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


# def get_index_of_user_in_times(user_id, index_type, start_year, start_month, end_year, end_month):
#     mysql_server = Mysql()
#     index_list = []
#     if index_type == '年':
#         for i in range(start_year, end_year + 1):
#             index_list.append([str(i), 0])
#         sql = 'SELECT year, sum(gasNum / userNum) FROM userdata ' \
#               'WHERE user_id = %s and year >= %s and year <= %s GROUP BY year ORDER BY year '
#         mysql_server.exe(sql, (user_id, start_year, end_year))
#     else:
#         for i in range(start_year * 12 + start_month, end_year * 12 + end_month + 1):
#             index_list.append([str(i // 12) + '/' + str((i - 1) % 12 + 1), 0])
#         sql = 'SELECT year, month, sum(gasNum / userNum) FROM userdata ' \
#               'WHERE user_id = %s and (year, month) >= (%s, %s) and (year, month) <= (%s, %s) ' \
#               'GROUP BY year, month order by year, month'
#         mysql_server.exe(sql, (user_id, start_year, start_month, end_year, end_month))
#     for row in mysql_server.results():
#         if index_type == '年':
#             index_list[row[0] - start_year][1] = float('{:.2f}'.format(row[1]))
#         else:
#             index_list[(row[0] * 12 + row[1]) - (start_year * 12 + start_month)][1] = float('{:.2f}'.format(row[2]))
#     return index_list


def get_weather_in_times(index_type, start_year, start_month, start_day, end_year, end_month, end_day):
    mysql_server = Mysql()
    weather_list = []
    weather_dict = {}
    if index_type == '年':
        for i in range(start_year, end_year + 1):
            weather_list.append([str(i)])
        sql = 'SELECT YEAR(date), AVG(max), AVG(min), AVG(ord) FROM weather ' \
              'WHERE YEAR(date) >= %s and YEAR(date) <= %s GROUP BY YEAR(date) ORDER BY YEAR(date)'
        mysql_server.exe(sql, (start_year, end_year))
    elif index_type == '月':
        for i in range(start_year * 12 + start_month, end_year * 12 + end_month + 1):
            weather_list.append([str(i // 12) + '/' + str((i - 1) % 12 + 1)])
        sql = 'SELECT YEAR(date), MONTH(date), AVG(max), AVG(min), AVG(ord) FROM weather ' \
              'WHERE (YEAR(date), MONTH(date)) >= (%s, %s) and (YEAR(date), MONTH(date)) <= (%s, %s) ' \
              'GROUP BY YEAR(date), MONTH(date) order by YEAR(date), MONTH(date)'
        mysql_server.exe(sql, (start_year, start_month, end_year, end_month))
    elif index_type == '日' or index_type == '周' or index_type == '小时':
        # dayfrom = datetime.datetime.strptime("%d-%d-%d" % (start_year, start_month, start_day), '%Y-%m-%d').date()
        # dayto = datetime.datetime.strptime("%d-%d-%d" % (end_year, end_month, end_day), '%Y-%m-%d').date()
        # dayscount = (dayto - dayfrom).days
        # for i in range(dayscount):
        #     d = dayfrom + datetime.timedelta(days=i)
        # weather_dict["%d/%d/%d" % (d.year, d.month, d.day)] = []
        sql = 'SELECT YEAR(date), MONTH(date), DAY(date), AVG(max), AVG(min), AVG(ord) FROM weather ' \
              'WHERE (YEAR(date), MONTH(date), DAY(date)) >= (%s, %s, %s) and (YEAR(date), MONTH(date), DAY(date)) <= (%s, %s, %s) ' \
              'GROUP BY YEAR(date), MONTH(date), DAY(date) order by YEAR(date), MONTH(date), DAY(date)'
        mysql_server.exe(sql, (start_year, start_month, start_day, end_year, end_month, end_day))
    for row in mysql_server.results():
        if index_type == '年':
            weather_list[row[0] - start_year].extend([row[1], row[2], row[3]])
        elif index_type == '月':
            weather_list[(row[0] * 12 + row[1]) - (start_year * 12 + start_month)].extend([row[2], row[3], row[4]])
        elif index_type == '日' or index_type == '周' or index_type == '小时':
            # weather_dict["%d/%d/%d" % (row[0], row[1], row[2])] = [row[3], row[4], row[5]]
            weather_list.append(["%d/%d/%d" % (row[0], row[1], row[2]), row[3], row[4], row[5]])

    return weather_list


def get_one_year_user_number(user_id, year):
    sql = 'SELECT u.year, u.month, u.day, u.hour, u.userNum From userdata u where u.user_id = %s and u.year = %s'
    params = (user_id, year)
    mysql_server = Mysql()
    mysql_server.exe(sql, params)
    results = {}
    for row in mysql_server.results():
        if row[0] in results:
            if row[1] in results[row[0]]:
                if row[2] in results[row[0]][row[1]]:
                    if row[3] in results[row[0]][row[1]][row[2]]:
                        pass
                    else:
                        results[row[0]][row[1]][row[2]][row[3]] = row[4]
                else:
                    results[row[0]][row[1]][row[2]] = {row[3]:
                                                           row[4]
                                                       }
            else:
                results[row[0]][row[1]] = {row[2]:
                                               {row[3]:
                                                    row[4]
                                                }
                                           }
        else:
            results[row[0]] = {row[1]:
                                   {row[2]:
                                        {row[3]:
                                             row[4]
                                         }
                                    }
                               }

    time_gas = results
    all = 0
    if year in time_gas:
        mts = time_gas[year]
        mts_keys = mts.keys()
        if 0 in mts_keys:
            all = mts[0][0][0]
        else:
            for m in mts_keys:
                days = mts[m]
                days_keys = days.keys()
                if 0 in days_keys:
                    all = days[0][0]
                else:
                    for d in days_keys:
                        hours = days[d]
                        hours_keys = hours.keys()
                        if 0 in hours_keys:
                            all = hours[0]
                        else:
                            for h in hours_keys:
                                all = hours[h]

    return all


def get_many_year_user_number(user_id, year):
    sql = 'SELECT u.year, u.month, u.day, u.hour, u.userNum From userdata u where u.user_id = %s and u.year <= %s'
    params = (user_id, year)
    mysql_server = Mysql()
    mysql_server.exe(sql, params)
    results = {}
    for row in mysql_server.results():
        if row[0] in results:
            if row[1] in results[row[0]]:
                if row[2] in results[row[0]][row[1]]:
                    if row[3] in results[row[0]][row[1]][row[2]]:
                        pass
                    else:
                        results[row[0]][row[1]][row[2]][row[3]] = row[4]
                else:
                    results[row[0]][row[1]][row[2]] = {row[3]:
                                                           row[4]
                                                       }
            else:
                results[row[0]][row[1]] = {row[2]:
                                               {row[3]:
                                                    row[4]
                                                }
                                           }
        else:
            results[row[0]] = {row[1]:
                                   {row[2]:
                                        {row[3]:
                                             row[4]
                                         }
                                    }
                               }

    time_gas = results
    year_dict = {}
    for y in time_gas.keys():
        all = 0
        if y in time_gas:
            mts = time_gas[y]
            mts_keys = mts.keys()
            if 0 in mts_keys:
                all = mts[0][0][0]
            else:
                for m in mts_keys:
                    days = mts[m]
                    days_keys = days.keys()
                    if 0 in days_keys:
                        all = days[0][0]
                    else:
                        for d in days_keys:
                            hours = days[d]
                            hours_keys = hours.keys()
                            if 0 in hours_keys:
                                all = hours[0]
                            else:
                                for h in hours_keys:
                                    all = hours[h]
        year_dict[y] = all

    return year_dict
