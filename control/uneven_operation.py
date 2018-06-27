from database.sqlquery import get_avg_gas


def search_uneven(user_id, timeType, search_time):
    uneven = 0
    if timeType == "月":
        year_avg = get_avg_gas(user_id, "年", search_time)
        month_avg = get_avg_gas(user_id, "月", search_time)
        uneven = month_avg / year_avg
        # return year_avg, month_avg, uneven
    elif timeType == "周":
        week_avg = get_avg_gas(user_id, "周", search_time)
        day = 24 * get_avg_gas(user_id, "日", search_time)
        uneven = day / week_avg
        # return week_avg, day, uneven
    elif timeType == "日":
        month_avg = get_avg_gas(user_id, "月", search_time)
        day = 24 * get_avg_gas(user_id, "日", search_time)
        uneven = day / month_avg
        # return month_avg, day, uneven
    elif timeType == "小时":
        day_avg = get_avg_gas(user_id, "日", search_time)
        hour = get_avg_gas(user_id, "小时", search_time)
        uneven = hour / day_avg

        # return day_avg, hour, uneven
    return uneven
