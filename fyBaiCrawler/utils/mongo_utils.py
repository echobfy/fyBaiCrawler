# -*- coding: utf-8 -*-
import pymongo


class MongoUtils(object):

    def __init__(self, host='localhost', port=27017):
        self.client = pymongo.MongoClient(host, port)
        self.cursor = set()

    def get_collection(self, db, coll):
        db = self.client[db]
        return db[coll]

    def close(self):
        self.client.close()



