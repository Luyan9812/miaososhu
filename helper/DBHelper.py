import time
import pymysql
import logging

from environs import Env


class MysqlHelper(object):
    """ 操作 mysql 数据库的辅助类 """

    def __init__(self, dbname):
        env = Env()
        env.read_env()
        host = env.str('SQL_HOST')
        port = env.int('SQL_PORT')
        user = env.str('SQL_USER')
        password = env.str('SQL_PASSWORD')
        self.db = pymysql.connect(host=host, port=port,
                                  user=user, password=password, db=dbname)
        self.cursor = self.db.cursor()

    def execute(self, sql):
        """ 执行 sql 语句 """
        try:
            self.cursor.execute(sql)
        except pymysql.err.Error as e:
            logging.exception(e)

    def insert(self, table_name, data: dict):
        """ 插入数据 """
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f'INSERT INTO {table_name} ({keys}) VALUES ({values}) '

        try:
            self.cursor.execute(sql, tuple(data.values()))
            insert_id = self.cursor.lastrowid
            self.db.commit()
            return insert_id
        except pymysql.err.Error as e:
            logging.exception(e)
            self.db.rollback()
        return -1

    def delete(self, table_name, condition):
        """ 删除数据 """
        if not condition: return
        sql = f'DELETE FROM {table_name} WHERE {condition} '

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except pymysql.err.Error as e:
            logging.exception(e)
            self.db.rollback()

    def update(self, table_name: str, data: dict, condition: str):
        """ 更新数据 """
        sql = f'UPDATE {table_name} SET '
        for i, k in enumerate(data):
            if i > 0: sql += ', '
            sql += f'{k} = %s'
        sql = sql % tuple(data.values())
        sql += f' WHERE {condition} '

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except pymysql.err.Error as e:
            logging.exception(e)
            self.db.rollback()

    def query_list(self, table_name, condition, order_by=None, limit=None, fields=None):
        """ 查询数据，返回列表 """
        array = []
        qf = ','.join(fields) if fields else '*'
        sql = f'SELECT {qf} FROM {table_name} WHERE {condition} '
        if order_by:
            sql += f'ORDER BY {order_by} '
        if limit:
            sql += f'LIMIT {limit} '

        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            while row:
                array.append(row)
                row = self.cursor.fetchone()
            return array
        except pymysql.err.Error as e:
            logging.exception(e)

    def query_one(self, table_name, condition, order_by=None, limit=None, fields=None):
        """ 查询一条数据 """
        qf = ','.join(fields) if fields else '*'
        sql = f'SELECT {qf} FROM {table_name} WHERE {condition} '
        if order_by:
            sql += f'ORDER BY {order_by} '
        if limit:
            sql += f'LIMIT {limit} '

        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except pymysql.err.Error as e:
            logging.exception(e)

    def count(self, table_name, condition):
        """ 统计数据数量 """
        sql = f'SELECT COUNT(*) FROM {table_name} WHERE {condition} '
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()[0]
        except pymysql.err.Error as e:
            logging.exception(e)

    def is_in(self, table_name, condition):
        """ 判断数据是否存在 """
        return self.count(table_name=table_name, condition=condition) > 0

    def onclose(self):
        """ 关闭数据库 """
        self.db.close()


def main():
    total_time = 0
    helper = MysqlHelper(dbname='miao_novel')
    for i in range(50):
        begin = time.time()
        helper.query_list('catalogue', 'book_id=1 ')
        end = time.time()
        total_time += (end - begin)
    print(total_time / 50)
    helper.onclose()


if __name__ == '__main__':
    main()
