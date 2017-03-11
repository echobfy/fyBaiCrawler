# -*- coding: utf-8 -*-

from mongo_utils import MongoUtils
import pycurl
import json
import time
import datetime
from bson.objectid import ObjectId

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class ESIndex(object):

    def __init__(self):
        self.curl = pycurl.Curl()

    def index(self, url, doc):
        if not isinstance(doc, str):
            doc = json.dumps(doc)
        print doc
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.POSTFIELDS, doc)
        curl.perform()

        print curl.getinfo(pycurl.HTTP_CODE)


if __name__ == '__main__':
    es = ESIndex()
    mongo_client = MongoUtils("mongodb://localhost:27017/itjuzi")
    print 'connected mongodb'
    coll = mongo_client.get_collection("company_detail")

    for i, doc in enumerate(coll.find()):
        print doc['_id']
        del doc['_id']

        es.index("localhost:9200/company/itjuzi", doc)
    mongo_client.close()




