# -*- coding: utf-8 -*-

import json
import logging
import scrapy
from scrapy import Field
from scrapy.cmdline import execute
from scrapy.http.request.form import FormRequest


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'itjuzi_company_api'])


class CompanyItem(scrapy.Item):
    com_id = Field()
    com_name = Field()
    com_sec_name = Field()
    com_registered_name = Field()
    com_logo = Field()
    com_video = Field()
    com_des = Field()
    com_url = Field()
    com_cat_id = Field()
    com_sub_cat_id = Field()
    com_born_year = Field()
    com_born_month = Field()
    com_prov = Field()
    com_city = Field()
    com_fund_needs_id = Field()
    com_radar_juziindex = Field()


class CompanyListSpider(scrapy.Spider):
    name = "itjuzi_company_api"

    start_urls = [
        "http://openapi.itjuzi.com/company/get_company_list"
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_DELAY": 5,
        "DOWNLOADER_MIDDLEWARES": {
            'fyBaiCrawler.middlewares.access_token_middleware.AccessTokenMiddleware': 2
        },
        "APP_ID": "app_id",
        "APP_KEY": "app_key",
        "ACCESS_TOEKN_URL": "http://openapi.itjuzi.com/oauth2.0/get_access_token",
        "EXPIRE_IN_SECOND": 3600,
        "ADVANCED_EXPIRE_IN_SECOND": 600,   # 6 minutes
        "DOWNLOAD_HANDLERS": {
            'http': "fyBaiCrawler.downloader.handlers.my_handler.MyHandler",
        },
    }

    MONGO_URI = "mongodb://localhost:27017/itjuzi1"
    MONGO_SUCC_STORE_COLLECTION = "CompanyItem"

    def start_requests(self):
        for start_url in self.start_urls:
            for page in range(1, 600):
                yield FormRequest(start_url,
                                  formdata={
                                      "limit": '100',
                                      "page": str(page)
                                  }
                        )
                logging.debug(' ---> Yield Request for page-{page}'.format(page=page))

    def parse(self, response):
        records = json.loads(response.body).get('data', [])
        if not records:
            print response.body
        for record in records:
            item = CompanyItem()
            for key, value in record.items():
                item[key] = value

            yield item
























