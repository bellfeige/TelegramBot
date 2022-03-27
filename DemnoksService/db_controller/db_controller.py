import json
import sqlite3
import os
from datetime import date, datetime
import random
import string

from DemnoksService.tele_bot.tele_bot import TeleBot


class DBcontroller(TeleBot):
    def __init__(self, db_name='DB.db', db_path='.', conn=None):
        super().__init__(self)
        self.db_name = db_name
        self.db_path = db_path
        self.conn = conn

    @staticmethod
    def index_generator(size=15, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
        except Exception as e:
            print(e)
        self.conn = conn
        # return conn

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Exception as e:
            print(e)

    def init_db(self, create_table_sql):
        # create_table_sql_example = '''
        # CREATE TABLE IF NOT EXISTS table_name (
        #                                     id integer PRIMARY KEY,
        #                                     field1 text NOT NULL,
        #                                     field2 text NOT NULL,
        #                                     field3 text NULL,
        #                                 );
        # '''

        self.create_connection()
        TeleBot.find_file(file=self.db_name, path=self.db_path)
        if self.conn is not None:
            with self.conn:
                self.create_table(create_table_sql)
        else:
            # print("Error! cannot create the database connection.")
            raise Exception("Error! cannot create the database connection.")

    def insert_into_table(self, insert_sql, data):
        # insert_sql_example = f''' INSERT INTO table_name (field1,field2,field3)
        #               VALUES(?,?,?) '''
        if self.conn is not None:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute(insert_sql, data)
                self.conn.commit()
        else:
            # print("Error! cannot create the database connection.")
            raise Exception("Error! cannot create the database connection.")

    def select_from_table(self, select_sql):
        # select_sql_example = f'''SELECT * FROM table_name'''

        if self.conn is not None:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute(select_sql)
                rows = cur.fetchall()
                # for row in rows:
                #     print(dict(row))
                return rows
        else:
            print("Error! cannot create the database connection.")
            raise SystemExit("Error! cannot create the database connection.", None)
            # return None
