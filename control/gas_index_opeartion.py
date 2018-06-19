from database.sqlquery import get_gas_index


def get_gas_index_from_database(user_id, index_type, year, month):
    return get_gas_index(user_id, index_type, year, month)
