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

    def __init__(self):
        self.mongo_client = MongoUtils()

    def open_spider(self, spider):
        if not spider.MONGO_DB or not spider.MONGO_COLLECTION:
            raise MongoException('mongo db and collection must in spider, if you want active this pipeline.')

        self.excluded_fields = spider.EXCLUDED_FIELDS if hasattr(spider, "EXCLUDED_FIELDS") else ()
        if self.excluded_fields:
            assert isinstance(self.excluded_fields, set)
            logging.info('the spider excluded fields -> {fields}.'.format(fields=self.excluded_fields))
        self.coll = self.mongo_client.get_collection(spider.MONGO_DB, spider.MONGO_COLLECTION)

    def process_item(self, item, spider):
        doc = {}
        for key, value in item.items():
            if key not in self.excluded_fields:
                doc[key] = value
        self.coll.insert(doc)

    def close_spider(self, spider):
        self.mongo_client.close()

