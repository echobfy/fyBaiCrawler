# -*- coding: utf-8 -*-

from mongo_utils import MongoUtils
import pycurl
import json
import time
import datetime

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
    mongo_client = MongoUtils("mongodb://10.13.93.251:27017/DB973")
    print 'connected mongodb'
    coll = mongo_client.get_collection("BaiduNews")
    for i, doc in enumerate(coll.find()):
        # doc['downDate'] = doc['downDate'].strftime('%Y-%m-%d %H:%M:%S')
        doc['pubDate'] = int(time.mktime(doc['pubDate'].timetuple()) * 1000)
        doc['downDate'] = int(time.mktime(datetime.datetime.strptime(doc['downDate'], '%Y-%m-%d %H:%M:%S').timetuple()) * 1000)
        doc['_id'] = str(doc['_id'])
        doc['mongoId'] = doc['_id']
        del doc['_id']

        print i
        if not doc['content']: continue
        es.index("10.13.93.251:9200/huaner/baidu", doc)
        # break





