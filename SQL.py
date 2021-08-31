# 1. 连接数据库，
import pymysql

class to_mysql:
    def __init__(self,host="localhost",user="root",password= "12346",db="helloTest",charset="utf8"):
        self.talble = ""
        self.host = host,
        self.user = user,
        self.password =password,
        self.db = db,
        self.charset = charset,
        self.cur = '',
        try :
            conn = pymysql.connect(
            host='localhost',
            user='root',
            password='redhat',
            db='helloTest',
            charset='utf8',
        )
            self.cur = conn.cursor()
        except Exception as  e :
            print(e)

    # def creat_table(self):
    #     try:
    #         creat_table_sql = "creat table test (id in, name carchar(30));"
    #         self.cur.execute(creat_table_sql)
    #
    #     except Exception as e:
    #         print(e)
    #
    def insert(self):
        table =""
        val = ""
        try:
            insert = " insert into " + table + " values " + val + ";"
        except Exception as e:
            print(e)

    # def search(self):
