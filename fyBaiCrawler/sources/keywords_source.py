# -*- coding: utf-8 -*-
import pymongo
from bson.objectid import ObjectId

from fyBaiCrawler.utils.mongo_utils import MongoUtils


class KeywordsSource(object):
    def get_doc(self, db, coll_name):
        raise NotImplemented


class FromMongo(KeywordsSource):
    def __init__(self, mongo_uri):
        self.mongo_client = MongoUtils(mongo_uri)

    def get_doc(self, coll_name, mongo_id=None):
        coll = self.mongo_client.get_collection(coll_name)

        if mongo_id:
            return coll.find({'_id': ObjectId(mongo_id)})
        return coll.find(timeout=False)

    def close(self):
        self.mongo_client.close()

