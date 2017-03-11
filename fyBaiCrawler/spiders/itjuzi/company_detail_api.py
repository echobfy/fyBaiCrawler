# -*- coding: utf-8 -*-
import json
import scrapy
import logging
from scrapy import Field
from scrapy.cmdline import execute
from scrapy.http.request.form import FormRequest
from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.spiders.itjuzi.company_list_api import CompanyListSpider


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'itjuzi_company_detail'])


class CompanyDetail(scrapy.Item):
    com_id = Field()
    com_name = Field()
    com_sec_name = Field()
    com_registered_name = Field()
    com_logo = Field()
    com_logo_archive = Field()
    com_video = Field()
    com_des = Field()
    com_url = Field()
    com_born_year = Field()
    com_born_month = Field()
    com_prov = Field()
    com_city = Field()
    com_status_id = Field()
    com_stage_id = Field()
    com_fund_needs_id = Field()
    round_id = Field()
    com_radar_juziindex = Field()
    com_weibo_url = Field()
    com_weixin_id = Field()
    com_cont_tel = Field()
    com_cont_email = Field()
    com_cont_addr = Field()

    scale = Field()
    cat = Field()
    subcat = Field()
    tag = Field()
    team = Field()
    product = Field()
    invest = Field()
    news = Field()
    similar_company = Field()


class CompanyDetailSpider(scrapy.Spider):
    name = "itjuzi_company_detail"

    start_urls = [
        "http://openapi.itjuzi.com/company/get_company_info"
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
        "ADVANCED_EXPIRE_IN_SECOND": 600,       # 6 minutes
        "DOWNLOAD_HANDLERS": {
            'http': "fyBaiCrawler.downloader.handlers.my_handler.MyHandler",
        },
    }

    MONGO_URI = "mongodb://localhost:27017/itjuzi1"
    MONGO_SUCC_STORE_COLLECTION = "CompanyDetail"

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection(CompanyListSpider.MONGO_SUCC_STORE_COLLECTION)
        for start_url in self.start_urls:
            for i, doc in enumerate(mongo_collection.find()):
                if i > 100: break
                if not doc.get('com_id'):
                    logging.warning(' ---> no com_id in doc for {com_id}:{com_name}.'.
                                    format(com_id=doc.get('com_id'), com_name=doc.get('com_name')))
                    continue
                yield FormRequest(start_url,
                                  formdata={
                                      "com_id": doc['com_id'],
                                  },
                                  meta={
                                      'com_name': doc.get('com_id'),
                                      'com_id': doc.get('com_name')
                                  }
                )
        mongo_client.close()

    def parse(self, response):
        record = json.loads(response.body).get('data', {})
        if not record:
            logging.warning(' ----> no thing in response for {com_id}:{com_name}.'
                            .format(com_id=response.meta.get('com_id'), com_name=response.meta.get('com_name')))
            return

        item = CompanyDetail()
        for key, value in record.items():
            item[key] = value
        yield item





























