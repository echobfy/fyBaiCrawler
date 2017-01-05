# -*- coding: utf-8 -*-
import json
import logging
import scrapy
from scrapy.http.request import Request
from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.spiders.itjuzi.company_detail_api import CompanyDetailSpider


class CompanyUrlSpider(scrapy.Spider):
    name = "company_url_spider"

    MONGO_URI = "mongodb://localhost:27017/itjuzi"
    MONGO_STORE_COLLECTION = "company_detail_more"

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
    }

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection(CompanyDetailSpider.MONGO_STORE_COLLECTION)
        for doc in mongo_collection.find():
            if not doc.get('com_url'):
                logging.info('')
                continue
            yield Request(doc['com_url'], meta={'company': doc})
        mongo_client.close()

    def parse(self, response):
        pass