#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pymysql, os, sys, time, _thread
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings

class BasePymysqlPool(object):
    def __init__(self, host, port, user, password, db_name=None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db_name
        self.conn = None
        self.cursor = None


class MyPymysqlPool(BasePymysqlPool):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
    """

    def __init__(self, conf_name=None):
        #self.conf = Config("dbconfig.cfg").get_content(conf_name)
        self.conf = settings[conf_name]
        super(MyPymysqlPool, self).__init__(**self.conf)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self.pool = self.create_pool()

    def create_pool(self):
        """
        @summary: 创建连接池
        @return conn_pool
        """
        pool = PooledDB(creator=pymysql,
                        mincached=3,
                        maxcached=20,
                        host=self.db_host,
                        port=self.db_port,
                        user=self.user,
                        passwd=self.password,
                        db=self.db,
                        use_unicode=False,
                        charset="utf8",
                        cursorclass=DictCursor)
        return pool

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询sql，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        if param is None:
            count = cursor.execute(sql)
        else:
            count = cursor.execute(sql, param)
        if count > 0:
            result = cursor.fetchall()
        else:
            result = -1
        cursor.close()
        conn.close()
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询sql，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        if param is None:
            count = cursor.execute(sql)
        else:
            count = cursor.execute(sql, param)
        if count > 0:
            result = cursor.fetchone()
            result = [result]
        else:
            result = -1
        cursor.close()
        conn.close()
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询sql，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        if param is None:
            count = cursor.execute(sql)
        else:
            count = cursor.execute(sql, param)
        if count > 0:
            result = cursor.fetchmany(num)
        else:
            result = -1
        cursor.close()
        conn.close() 
        return result

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的sql格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            count = cursor.executemany(sql, values)
            conn.commit()
        except:
            conn.rollback()
        cursor.close()
        conn.close() 
        return count

    def __query(self, sql, param=None):
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            if param is None:
                count = cursor.execute(sql)
            else:
                count = cursor.execute(sql, param)
            conn.commit()
        except:
            count = -1
            conn.rollback()
        cursor.close()
        conn.close()
        return count

#处理事物，2022-06-27添加，hl
    def execAffairs(self, sqllist, param=None):
        conn = self.pool.connection()
        cursor = conn.cursor()
        count = 0
        try:
            if param is None:
                for sql in sqllist:
                    cursor.execute(sql)
            else:
                for sql in sqllist:
                    cursor.execute(sql, param)
            conn.commit()
        except:
            count = -1
            conn.rollback()
        cursor.close()
        conn.close()
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: sql格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: sql格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: sql格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)



def decodeData(data):
    try:
        for dic in data:
            for key in dic.keys():
                if isinstance(dic[key], bytes):
                    dic[key] = dic[key].decode('utf-8')
    except:
        return None
    return data

def testthread(name):

    params = {"id":2}
    #sqlAll = "select name from FunType where id=%s"
    #result = mysql.getAll(sqlAll, (2,))
    #sqlAll = "select name from FunType where id=%(id)s"
    #result = mysql.getAll(sqlAll, params)
    sqlAll = "select id,name from FunType"
    result = mysql.getOne(sqlAll)
    result = decodeData(result)
    print(result)
'''
    result = mysql.getMany(sqlAll, 2)
    print(result)

    result = mysql.getOne(sqlAll)
    print(result)
 
    sqlinsert = "insert into ltag(tag) values ('%s')"%name
    print(sqlinsert)
    mysql.insert(sqlinsert)  
'''

if __name__ == '__main__':
    #mysql = MyPymysqlPool("dbmysql")
    _thread.start_new_thread(testthread, ("thread-3", ))
    #_thread.start_new_thread(testthread, ("thread-4", ))

    time.sleep(4)
    # mysql.insert("insert into myTest.aa set a=%s", (1))
