import pymysql


class Mysql(object):

    db = 0
    cursor = 0
    n_exe = 0
    n_commit = 0

    def __init__(self):
        self.db = 0
        self.cursor = 0
        self.n_exe = 0
        self.n_commit = 0
        self.openSQL()
        pass

    def openSQL(self):
        # 打开数据库连接
        self.db = pymysql.connect(
            host="localhost", user="root", passwd="1q2w3e4r", db="nis_website", charset='UTF8')
        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        # print("数据库连接成功", self.db, flush=True)

    def exe(self, string, args=None):
        if args:
            self.cursor.execute(string, args)
        else:
            self.cursor.execute(string)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def results(self):
        # 使用 fetchone() 方法获取一条数据库。
        return self.cursor.fetchall()

    def closeSQL(self):
        # 关闭数据库连接
        self.db.close()
