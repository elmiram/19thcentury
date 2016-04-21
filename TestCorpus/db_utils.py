__author__ = 'elmira'

import MySQLdb as mdb
import codecs

class Database(object):
    def __init__(self):
        self._connection = mdb.connect('', 'webcorpo_corpora', 'yedLurt3', '19thcentury', charset='utf8')

    def commit(self):
        self._connection.commit()

    def execute(self, q):
        self.cur = self._connection.cursor()  # mdb.cursors.DictCursor
        self.cur.execute(q)
        res = self.cur.fetchall()
        self.cur.close()
        return res