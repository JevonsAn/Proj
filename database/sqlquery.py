from database.sqlconnection import Mysql


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


def insert_news(newstype, newsTitle, newsContent, newsFabiaoren='null'):
    mysqlserver = Mysql()
    # mysqlserver.openSQL()
    sql = "insert into news(type, title, content, fabiaoren) values('%s', '%s', '%s', '%s');"
    res = [True, '']
    try:
        mysqlserver.exe(sql,  (newstype, newsTitle,
                               newsContent, newsFabiaoren))
        mysqlserver.commit()
    except Exception as e:
        res = [False, e]
    finally:
        mysqlserver.closeSQL()
        return res