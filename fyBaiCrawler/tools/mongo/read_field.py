# -*- encoding: utf-8 -*-

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.utils.excel_utils import ExcelWriter


class ReadFieldFromMongo(object):

    def __init__(self, mongo_uri, collection):
        self.mongo_client = MongoUtils(mongo_uri)
        self.coll = collection

    def read_from_mongo(self, *fields):
        field_set = set(fields)
        coll = self.mongo_client.get_collection(self.coll)

        for doc in coll.find():
            for field, value in doc.items():
                if field in field_set:
                    yield field, value

    def close(self):
        self.mongo_client.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    mongo_client = ReadFieldFromMongo('mongodb://localhost:27017/itjuzi', 'company_list')
    file_handler = ExcelWriter('data.xls')

    mongo_client.close()
    file_handler.close()



