# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy import Field
from scrapy.http.request.form import FormRequest
from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.spiders.itjuzi.company_list_api import CompanyListSpider


class CompanyDetailItem(scrapy.Item):
    com_id = Field()
    com_name = Field()
    com_sec_name = Field()
    com_registered_name = Field()
    com_logo = Field()
    com_logo_archive = Field()
    com_video = Field()
    com_url = Field()
    com_born_year = Field()
    com_born_month = Field()
    com_prov = Field()
    com_city = Field()
    com_status_id = Field()
    com_stage_id = Field()
    com_fund_needs_id = Field()
    com_radar_juziindex = Field()
    com_weibo_url = Field()
    com_weixin_id = Field()
    com_cont_tel = Field()
    com_cont_email = Field()
    com_cont_addr = Field()

    cat = Field()
    subcat = Field()
    tag = Field()
    team = Field()
    product = Field()
    invest = Field()
    news = Field()
    similar_company = Field()


class CompanyDetailSpider(scrapy.Spider):
    name = "itjuzi_company_list"

    start_urls = [
        "http://openapi.itjuzi.com/company/get_company_info"
    ]

    ACCESS_TOKEN = "your_access_token"

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_DELAY": 3,
    }

    MONGO_URI = "mongodb://localhost:27017/itjuzi"
    MONGO_STORE_COLLECTION = "company_detail"

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection(CompanyListSpider.MONGO_STORE_COLLECTION)
        for start_url in self.start_urls:
            for doc in mongo_collection.find():
                if not doc.get('com_id'):
                    continue
                yield FormRequest(start_url,
                                  headers={
                                      'Authorization': "Bearer " + self.ACCESS_TOKEN
                                  },
                                  formdata={
                                      "com_id": doc['com_id'],
                                  }
                )
        mongo_client.close()

    def parse(self, response):
        record = json.loads(response.body).get('data', {})
        if not record:
            return

        item = CompanyDetailItem()
        for key, value in record.items():
            item[key] = value
        yield item





























