from database.sqlquery import get_avg_gas


def search_uneven(user_id, timeType, search_time, time_gas=None):
    uneven = 0

    if timeType == "月":
        year_avg = get_avg_gas(user_id, "年", search_time, time_gas)
        month_avg = get_avg_gas(user_id, "月", search_time, time_gas)
        if year_avg == 0:
            res = [False, "没有年数据"]
            return res
        uneven = month_avg / year_avg
        # return year_avg, month_avg, uneven
    elif timeType == "周":
        week_avg = get_avg_gas(user_id, "周", search_time, time_gas)
        day = 24 * get_avg_gas(user_id, "日", search_time, time_gas)
        if week_avg == 0:
            res = [False, "没有周数据"]
            return res
        uneven = day / week_avg
        # return week_avg, day, uneven
    elif timeType == "日":
        month_avg = get_avg_gas(user_id, "月", search_time, time_gas)
        day = 24 * get_avg_gas(user_id, "日", search_time, time_gas)
        if month_avg == 0:
            res = [False, "没有月数据"]
            return res
        uneven = day / month_avg
        # return month_avg, day, uneven
    elif timeType == "小时":
        day_avg = get_avg_gas(user_id, "日", search_time, time_gas)
        hour = get_avg_gas(user_id, "小时", search_time, time_gas)
        if day_avg == 0:
            res = [False, "没有日数据"]
            return res
        uneven = hour / day_avg

        # return day_avg, hour, uneven
    res = [True, uneven]
    return res
