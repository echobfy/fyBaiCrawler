# -*- coding: utf-8 -*-

"""

"""

import re
import logging
import scrapy
from scrapy import Field
from scrapy.cmdline import execute
from scrapy.utils.misc import arg_to_iter
from scrapy.http.request.form import Request, FormRequest

from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.spiders.itjuzi.company_list_api import CompanyListSpider, CompanyItem


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'baidu_related_news'])


class BaiduRelatedNewsItem(CompanyItem, scrapy.Item):
    keyword_popularity = Field()


class BaiduRelatedNewsSpider(scrapy.Spider):
    name = "baidu_related_news"

    start_urls = [
        "https://www.baidu.com/s?wd="
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_DELAY": 3,
    }

    MONGO_URI = "mongodb://localhost:27017/itjuzi1"
    MONGO_SUCC_STORE_COLLECTION = "BaiduRelatedNewsItem"

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection(CompanyListSpider.MONGO_SUCC_STORE_COLLECTION)
        for i, doc in enumerate(mongo_collection.find(no_cursor_timeout=True)):
            if not doc.get('com_id'):
                logging.warning(' ---> no com_id in doc for {com_id}:{com_name}.'.
                                format(com_id=doc.get('com_id'), com_name=doc.get('com_name')))
                continue
            logging.debug(' ---> fetch request:{com_id}.'.format(com_id=doc.get('com_id')))

            for keyword in ['com_name', 'com_registered_name', 'com_sec_name']:
                com_name = doc.get(keyword)
                if com_name:
                    for req in self.start_requests_internal(doc.get(keyword), com_info=doc, com_name=com_name):
                        yield req
                    break
        mongo_client.close()

    def simplify_keyword(self, keyword):
        simplified_keyword = re.sub("(\(.*\))", "", keyword)
        return simplified_keyword if len(simplified_keyword) > 0 else keyword

    def start_requests_internal(self, keywords, **kwargs):
        for start_url in self.start_urls:
            for keyword in arg_to_iter(keywords):
                simplified_keyword = self.simplify_keyword(keyword)
                logging.debug(' ---> Yield Baidu Request for keyword-{keyword}'.format(keyword=simplified_keyword))
                yield Request(start_url + simplified_keyword, meta=kwargs)

    def parse(self, response):
        body = response.text
        match = re.search(u"百度为您找到相关结果约(.*)个", body)
        if match:
            number_of_related_news = match.group(1)
            keyword_popularity = long(number_of_related_news.replace(",", "")) / 1000000.0

            item = BaiduRelatedNewsItem()
            item['keyword_popularity'] = keyword_popularity
            for k, v in response.meta['com_info'].items():
                if k != '_id': item[k] = v
            yield item
        else:
            logging.warning(' ---> no related results in baidu for {com_name}.'
                            .format(com_name=response.meta['com_name']))




