# -*- encoding: utf-8 -*-

import os
import sys
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.tools.mongo.merge_polices import AttributeMergePolicy


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    # filename=BASE_DIR + '/logs/25pp/anaylse.log',
    # filemode='w'
)


class MergeRecord(object):

    def __init__(self, read1, read2, to1, to2):
        uri1, coll1 = read1
        uri2, coll2 = read2
        uri3, coll3 = to1
        uri4, coll4 = to2

        self.mongo_client1 = MongoUtils(uri=uri1)
        self.coll1 = self.mongo_client1.get_collection(coll1)

        self.mongo_client2 = MongoUtils(uri=uri2)
        self.coll2 = self.mongo_client2.get_collection(coll2)

        self.mongo_client3 = MongoUtils(uri=uri3)
        self.coll3 = self.mongo_client3.get_collection(coll3)

        self.mongo_client4 = MongoUtils(uri=uri3)
        self.coll4 = self.mongo_client4.get_collection(coll4)

        self.merge_polices = [AttributeMergePolicy()]

    def merge(self):
        docs = list(self.coll2.find())
        for doc in docs:
            doc['com_apps_apk'] = []

        for i, doc in enumerate(self.coll1.find()):
            logging.info(' {index} ====> {app_name}.'.format(index=i, app_name=doc.get('name')))
            flag = False
            for merge_policy in self.merge_polices:
                if merge_policy.merge(doc, docs):
                    flag = True
            if flag is False:
                self.coll4.insert(doc)

        for doc in docs:
            self.coll3.insert(doc)

    def close(self):
        self.mongo_client1.close()
        self.mongo_client2.close()
        self.mongo_client3.close()
        self.mongo_client4.close()


if __name__ == '__main__':
    uri = 'mongodb://localhost:27017/'
    merge_instance = MergeRecord(
        (uri + 'apps', "wandoujia_apk"),
        (uri + 'itjuzi', "company_list"),
        (uri + 'app_company', "app_company"),
        (uri + 'app_company', "failed")
    )

    merge_instance.merge()
    merge_instance.close()


