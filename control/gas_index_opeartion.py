from database.sqlquery import get_gas_index, get_weather_in_times


def get_gas_index_from_database(user_id, index_type, year, month):
    time_gas = get_gas_index(user_id, index_type, year, month)
    if index_type == "年":
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


def get_user_gasIndex_year_and_month(user_id, timeType, start_time, stop_time):
    # user = get_user_by_id(user_id)
    # unit = "%s / %s · %s" % (user["gasUnit"], user["userUnit"], timeType)
    gasIndex_list = []

    def timeChange(timeType, t):
        if timeType == "月":
            return "%d-%d" % (t[0], t[1])
        elif timeType == "年":
            return "%d" % t[0]

    all_time = {timeType: []}
    if timeType == "年":
        all_time[timeType] = [(x, 0) for x in range(int(start_time[:4]), int(stop_time[:4]) + 1)]
    elif timeType == "月":
        all_time[timeType] = [(int(start_time[:4]), m) for m in range(int(start_time[4:]), 13)] \
                             + [(x, m) for x in range(int(start_time[:4]) + 1, int(stop_time[:4])) for m in
                                range(1, 13)] \
                             + [(int(stop_time[:4]), m) for m in range(1, int(stop_time[4:]) + 1) if
                                start_time[:4] < stop_time[:4]]
    for t in all_time[timeType]:
        lt = []
        lt.append(timeChange(timeType, t))
        gasIndex = get_gas_index_from_database(user_id, timeType, *t)
        lt.append(gasIndex)
        gasIndex_list.append(lt)
    return gasIndex_list

def get_index_of_user_in_times_from_database(user_id, index_type, start_year, start_month, end_year, end_month):
    return get_user_gasIndex_year_and_month(user_id, index_type, "%4d%2d" % (start_year, start_month),
                                            "%4d%2d" % (end_year, end_month))


def get_weather_in_times_from_database(index_type, start_year, start_month, start_day, end_year, end_month, end_day):
    return get_weather_in_times(index_type, start_year, start_month, start_day, end_year, end_month, end_day)
