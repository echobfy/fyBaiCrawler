# -*- encoding: utf-8 -*-

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.utils.mongo_utils import MongoUtils


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


class WriteFieldIntoFile(object):

    def __init__(self, path):
        self.f = open(path, 'w')

    def write_into_file(self, line):
        self.f.write(line)

    def close(self):
        self.f.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    mongo_client = ReadFieldFromMongo('mongodb://localhost:27017/itjuzi', 'company_list')
    file_handler = WriteFieldIntoFile('dict.txt')

    dup = set()
    for field, value in mongo_client.read_from_mongo('com_name', 'com_prov'):
        res = value + " " + str(100) + '\n'
        if res not in dup:
            file_handler.write_into_file(res)
            dup.add(res)

    mongo_client.close()
    file_handler.close()



