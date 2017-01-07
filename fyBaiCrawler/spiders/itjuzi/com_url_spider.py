# -*- coding: utf-8 -*-
import json
import logging
import scrapy
from scrapy.cmdline import execute
from scrapy.http.request import Request
from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.analyse.web.web_policy import UrlAnaylsePolicy
from fyBaiCrawler.spiders.itjuzi.company_detail_api import CompanyDetailSpider


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'company_url_spider'])


class CompanyUrlSpider(scrapy.Spider):
    name = "company_url_spider"

    MONGO_URI = "mongodb://localhost:27017/itjuzi"
    MONGO_STORE_COLLECTION = "company_detail_more"

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_HANDLERS": {
            'http': 'fyBaiCrawler.downloader.selenium_handler.PhantomJSDownloadHandler',
            'https': 'fyBaiCrawler.downloader.selenium_handler.PhantomJSDownloadHandler',
        },
    }

    start_urls = [
        'https://www.baidu.com/',
        'http://www.cnblogs.com/BeginMan/p/3178103.html',
        'http://blog.chinaunix.net/uid-26000296-id-4461522.html'
    ]

    anaylse_policy = [UrlAnaylsePolicy()]

    # def start_requests(self):
    #     mongo_client = MongoUtils(uri=self.MONGO_URI)
    #     mongo_collection = mongo_client.get_collection(CompanyDetailSpider.MONGO_STORE_COLLECTION)
    #     for doc in mongo_collection.find():
    #         if not doc.get('com_url'):
    #             logging.info('')
    #             continue
    #         yield Request(doc['com_url'], meta={'company': doc})
    #     mongo_client.close()

    def parse(self, response):
        try:
            json_results = json.loads(response.body)
        except Exception as e:
            logging.error('{url} error...\n{error}'.format(url=response.request.url, error=str(e)))
            return
        page_data = json_results['HelloWorld']['entries']
        for policy in self.anaylse_policy:
            print policy.anaylse(page_data)

