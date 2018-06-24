from database.sqlquery import get_gas_index, get_index_of_user_in_times, get_weather_in_times


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


def get_index_of_user_in_times_from_database(user_id, index_type, start_year, start_month, end_year, end_month):
    return get_index_of_user_in_times(user_id, index_type, start_year, start_month, end_year, end_month)

def get_weather_in_times_from_database(index_type, start_year, start_month, end_year, end_month):
    return get_weather_in_times(index_type, start_year, start_month, end_year, end_month)
