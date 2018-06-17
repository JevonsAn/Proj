from database.sqlconnection import Mysql
from pymysql import IntegrityError


def get_oneNews(newsType, idnews):
    mysqlserver = Mysql()
    sql = "select title, content, time, fabiaoren from nis_website.news where type='%s' and idnews=%d;"
    mysqlserver.exe(sql,  (newsType, idnews))
    news = {}
    #print(mysqlserver.results(), flush=True)
    for row in mysqlserver.results():
        news['content'] = row[1]
        news['title'] = row[0]
        news['time'] = row[2]
        news['fabiaoren'] = row[3]
    mysqlserver.closeSQL()
    return news


def insert_user(userType, userName, gasUnit, userUnit, remark=''):
    mysqlserver = Mysql()
    # mysqlserver.openSQL()
    sql = "INSERT INTO `data`.`user` (`userType`, `userName`, `gasUnit`, `userUnit`) VALUES (%s, %s, %s, %s);"
    res = [True, '']
    try:
        mysqlserver.exe(sql, (userType, userName, gasUnit, userUnit))
        mysqlserver.commit()
    except Exception as e:
        res = [False, e]
    finally:
        mysqlserver.closeSQL()
        return res


def insert_weather(date, maxTemperature, minTemperature, avgTemperature):
    mysqlserver = Mysql()
    sql = 'INSERT INTO data.weather (date, max, min, ord) VALUES (%s, %s, %s, %s);'
    mysqlserver.exe(sql, (date, maxTemperature, minTemperature, avgTemperature))
    mysqlserver.commit()
    mysqlserver.closeSQL()
