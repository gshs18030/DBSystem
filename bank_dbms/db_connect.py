import pymysql as pms

from pymysql.cursors import DictCursor

def get_connection():
    return pms.connect(
        host="localhost",
        user="root",
        password="rlawogud2177",
        database="bank",
        charset="utf8",
        cursorclass=DictCursor,
        autocommit=False,
    )