# -*- coding: utf-8 -*-

"""

"""

import re
import logging
import scrapy
from scrapy import Field
from scrapy.cmdline import execute
from scrapy.http.request.form import Request
from scrapy.utils.misc import arg_to_iter


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'baidu_related_news'])


class BaiduRelatedNewsItem(scrapy.Item):
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
        for req in self.start_requests_internal(['滴滴出行']):
            yield req

    def simplify_keyword(self, keyword):
        simplified_keyword = re.sub("(\(.*\))", "", keyword)
        return simplified_keyword if len(simplified_keyword) > 0 else keyword

    def start_requests_internal(self, keywords):
        for start_url in self.start_urls:
            for keyword in arg_to_iter(keywords):
                simplified_keyword = self.simplify_keyword(keyword)
                logging.debug(' ---> Yield Baidu Request for keyword-{keyword}'.format(keyword=simplified_keyword))
                yield Request(start_url + simplified_keyword)

    def parse(self, response):
        body = response.text
        match = re.search(u"百度为您找到相关结果约(.*)个", body)
        if match:
            number_of_related_news = match.group(1)
            keyword_popularity = long(number_of_related_news.replace(",", "")) / 1000000.0

            item = BaiduRelatedNewsItem()
            item['keyword_popularity'] = keyword_popularity
            yield item
        else:
            pass




