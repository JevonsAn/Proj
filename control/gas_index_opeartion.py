from database.sqlquery import get_gas_index, get_index_of_user_in_times, get_weather_in_times


def get_gas_index_from_database(user_id, index_type, year, month):
    return get_gas_index(user_id, index_type, year, month)


def get_index_of_user_in_times_from_database(user_id, index_type, start_year, start_month, end_year, end_month):
    return get_index_of_user_in_times(user_id, index_type, start_year, start_month, end_year, end_month)

def get_weather_in_times_from_database(index_type, start_year, start_month, end_year, end_month):
    return get_weather_in_times(index_type, start_year, start_month, end_year, end_month)
