# -*- coding: utf-8 -*-
import json
import sys
import logging
import scrapy
from scrapy.cmdline import execute
from scrapy.http.request import Request
from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.analyse.web.web_policy import HTMLAnaylsePolicy
from fyBaiCrawler.spiders.itjuzi.company_list_api import CompanyListSpider

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'web_page_spider'])


class CompanyListWeb(scrapy.Item):
    com_id = scrapy.Field()
    web_page = scrapy.Field()


class CompanyUrlSpider(scrapy.Spider):
    name = "web_page_spider"

    MONGO_URI = "mongodb://localhost:27017/itjuzi"
    MONGO_SUCC_STORE_COLLECTION = "CompanyListWeb"

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_TIMEOUT": 180,  # 3mins
        "CONCURRENT_REQUESTS": 32,
        # 'HTTPERROR_ALLOW_ALL': True
    }

    # For Test
    start_urls = [
        # 'http://en.wison.com/',
        # 'http://www.hunliji.com/',
        # 'http://bbs.ngacn.cc/',
        'http://wodsadsa.cn'
    ]

    anaylse_policy = HTMLAnaylsePolicy()

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection(CompanyListSpider.MONGO_STORE_COLLECTION)
        for i, doc in enumerate(mongo_collection.find(no_cursor_timeout=True)):
            logging.debug(' {index} ======> {com_name}.'.format(index=i, com_name=doc.get('com_name')))
            if not doc.get('com_url'):
                logging.info(' ---> no com_url for {com_id}'.format(com_id=doc.get('com_id')))
                continue
            com_url = doc.get('com_url')
            if not (com_url.startswith('http') and ':' in com_url):
                logging.info(' ---> error com_url for {com_id}'.format(com_id=doc.get('com_id')))
                continue
            yield Request(doc['com_url'], meta={'com_info': doc})
        mongo_client.close()

    def parse(self, response):
        succ_item = CompanyListWeb()
        succ_item['com_id'] = response.meta['com_info']['com_id']
        succ_item['web_page'] = self.anaylse_policy.anaylse(response.body)
        yield succ_item

