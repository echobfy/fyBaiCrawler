# -*- coding: utf-8 -*-
import pymongo


class MongoUtils(object):

    def __init__(self, uri='mongodb://localhost:27017/bfy_test'):
        self.client = pymongo.MongoClient(uri)

    def get_collection(self, coll):
        return self.client.get_default_database()[coll]

    def close(self):
        self.client.close()



