# -*- coding: utf-8 -*-
import sys
import logging
from fyBaiCrawler.utils.mongo_utils import MongoUtils

reload(sys)
sys.setdefaultencoding('utf-8')

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MongoException(Exception):
    pass


class MongoPipeline(object):

    def open_spider(self, spider):
        if not spider.MONGO_URI and not spider.MONGO_SUCC_STORE_COLLECTION:
            raise MongoException('mongo db and collection must in spider, if you want active this pipeline.')
        self.excluded_fields = spider.EXCLUDED_FIELDS if hasattr(spider, "EXCLUDED_FIELDS") else ()
        if self.excluded_fields:
            assert isinstance(self.excluded_fields, set)
            logging.info('the spider excluded fields -> {fields}.'.format(fields=self.excluded_fields))
        self.mongo_client = MongoUtils(spider.MONGO_URI)

        self.succ_coll_str = spider.MONGO_SUCC_STORE_COLLECTION
        self.succ_coll = self.mongo_client.get_collection(spider.MONGO_SUCC_STORE_COLLECTION)

        if hasattr(spider, 'MONGO_FAIL_STORE_COLLECTION'):
            self.fail_coll_str = spider.MONGO_FAIL_STORE_COLLECTION
            self.fail_coll = self.mongo_client.get_collection(spider.MONGO_FAIL_STORE_COLLECTION)
        else:
            self.fail_coll_str = None
            self.fail_coll = None

    def process_item(self, item, spider):
        doc = {}
        for key, value in item.items():
            if key not in self.excluded_fields:
                doc[key] = value

        if item.__class__.__name__ == self.succ_coll_str:
            self.succ_coll.insert(doc)
        elif self.fail_coll and item.__class__.__name__ == self.fail_coll_str:
            self.fail_coll.insert(doc)

    def close_spider(self, spider):
        self.mongo_client.close()

