import datetime
from database.sqlquery import get_avg_gas, get_many_avg_gas


def search_uneven(user_id, timeType, search_time, time_gas=None):
    uneven = 0

    if timeType == "月":
        year_avg = get_avg_gas(user_id, "年", search_time, time_gas)
        month_avg = get_avg_gas(user_id, "月", search_time, time_gas)
        if year_avg == 0:
            res = [False, "没有年数据，或数据值为0"]
            return res
        uneven = month_avg / year_avg
        # return year_avg, month_avg, uneven
    elif timeType == "周":
        week_avg = get_avg_gas(user_id, "周", search_time, time_gas)
        day = 24 * get_avg_gas(user_id, "日", search_time, time_gas)
        if week_avg == 0:
            res = [False, "没有周数据，或数据值为0"]
            return res
        uneven = day / week_avg
        # return week_avg, day, uneven
    elif timeType == "日":
        month_avg = get_avg_gas(user_id, "月", search_time, time_gas)
        day = 24 * get_avg_gas(user_id, "日", search_time, time_gas)
        if month_avg == 0:
            res = [False, "没有月数据，或数据值为0"]
            return res
        uneven = day / month_avg
        # return month_avg, day, uneven
    elif timeType == "小时":
        day_avg = get_avg_gas(user_id, "日", search_time, time_gas)
        hour = get_avg_gas(user_id, "小时", search_time, time_gas)
        if day_avg == 0:
            res = [False, "没有日数据，或数据值为0"]
            return res
        uneven = hour / day_avg

        # return day_avg, hour, uneven
    res = [True, uneven]
    return res


def get_uneven_list(user_id, timeType, start_time, stop_time):
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
            return "%d-%d-%d : %d-%d时" % (year, month, day, hour - 1, hour)
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
            if start_time[:4] < stop_time[:4]:
                all_time[timeType] = ["%4d%2d" % (int(start_time[:4]), m) for m in range(int(start_time[4:6]), 13)] \
                                     + ["%4d%2d" % (x, m) for x in range(int(start_time[:4]) + 1, int(stop_time[:4])) for m
                                    in range(1, 13)] \
                                     + ["%4d%2d" % (int(stop_time[:4]), m) for m in range(1, int(stop_time[4:6]) + 1)]
            else:
                all_time[timeType] = ["%4d%2d" % (int(start_time[:4]), m) for m in
                                      range(int(start_time[4:6]), int(stop_time[4:6]) + 1)]
        elif timeType == "日":
            dayfrom = datetime.datetime.strptime(start_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayto = datetime.datetime.strptime(stop_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayscount = (dayto - dayfrom).days
            all_time[timeType] = []
            for i in range(dayscount + 1):
                d = dayfrom + datetime.timedelta(days=i)
                all_time[timeType].append("%4d%2d%2d" % (d.year, d.month, d.day))

        elif timeType == "周":
            dayfrom = datetime.datetime.strptime(start_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayto = datetime.datetime.strptime(stop_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayscount = (dayto - dayfrom).days
            all_time[timeType] = []
            for i in range(dayscount + 1):
                d = dayfrom + datetime.timedelta(days=i)
                all_time[timeType].append("%4d%2d%2d" % (d.year, d.month, d.day))

        elif timeType == "小时":
            dayfrom = datetime.datetime.strptime(start_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayto = datetime.datetime.strptime(stop_time[:8].replace(" ", "0"), '%Y%m%d').date()
            dayscount = (dayto - dayfrom).days
            all_time[timeType] = []
            for i in range(dayscount + 1):
                d = dayfrom + datetime.timedelta(days=i)
                for h in range(1, int(stop_time[8:10]) + 1):
                    all_time[timeType].append("%4d%2d%2d%2d" % (d.year, d.month, d.day, h))

        uneven_list = []

        for t in all_time[timeType]:
            lt = []
            # lt.append(user["userType"])
            # lt.append(user["userName"])
            lt.append(timeChange(timeType, t))
            lres = search_uneven(user_id, timeType, t, time_gas)
            if lres[0] is False:
                continue
            else:
                lt.append(lres[1])
            uneven_list.append(lt)
        res[1] = uneven_list
    except PermissionError as e:
        res[0] = False
        res[1] = str("没有写入文件的权限，可能是文件未关闭导致")
    except Exception as e:
        raise e
        # res[0] = False
        # print(e)
        # res[1] = str(e)
    return res
