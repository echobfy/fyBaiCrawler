# -*- coding: utf-8 -*-
import json
import logging
import scrapy
from scrapy.cmdline import execute
from scrapy.http.request import Request
from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.analyse.web.web_policy import UrlAnaylsePolicy
from fyBaiCrawler.spiders.itjuzi.company_list_api import CompanyListSpider


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'company_url_spider'])


class CompanyListWeb(scrapy.Item):
    com_info = scrapy.Field()
    web_page = scrapy.Field()


class FailCompanyListWeb(scrapy.Item):
    com_info = scrapy.Field()


class CompanyUrlSpider(scrapy.Spider):
    name = "company_url_spider"

    MONGO_URI = "mongodb://localhost:27017/itjuzi"
    MONGO_SUCC_STORE_COLLECTION = "CompanyListWeb"
    MONGO_FAIL_STORE_COLLECTION = "FailCompanyListWeb"

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_HANDLERS": {
            'http': 'fyBaiCrawler.downloader.selenium_handler.PhantomJSDownloadHandler',
            'https': 'fyBaiCrawler.downloader.selenium_handler.PhantomJSDownloadHandler',
        },
    }

    # For Test
    start_urls = [
        'http://www.hunliji.com/?sempp'
    ]

    anaylse_policy = UrlAnaylsePolicy()

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection(CompanyListSpider.MONGO_STORE_COLLECTION)
        for i, doc in enumerate(mongo_collection.find(no_cursor_timeout=True)):
            logging.debug(' {index} ======> {com_name}.'.format(index=i, com_name=doc.get('com_name')))
            if not doc.get('com_url'):
                logging.info(' ---> no com_url for {com_id}'.format(com_id=doc.get('com_id')))
                continue
            yield Request(doc['com_url'], meta={'com_info': doc})
        mongo_client.close()

    def parse(self, response):
        try:
            json_results = json.loads(response.body)
        except Exception as e:
            logging.error('{url} error...\n{error}'.format(url=response.request.url, error=str(e)))
            fail_item = FailCompanyListWeb()
            fail_item['com_info'] = response.meta['com_info']
            yield fail_item
        else:
            succ_item = CompanyListWeb()
            succ_item['com_info'] = response.meta['com_info']
            page_data = json_results['HelloWorld']['entries']
            succ_item['web_page'] = self.anaylse_policy.anaylse(page_data)
            yield succ_item

