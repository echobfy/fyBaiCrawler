# -*- coding: utf-8 -*-

import logging
import scrapy
import string
import re
from scrapy.cmdline import execute
from scrapy.http import Request
from bs4 import BeautifulSoup

from fyBaiCrawler.utils.mongo_utils import MongoUtils


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'wandoujia'])


class CompanyAndApk(scrapy.Item):
    """抓取成功的App，将整合信息
    """
    wandoujia_link = scrapy.Field()
    com_url = scrapy.Field()
    com_name = scrapy.Field()
    app_info = scrapy.Field()


class FailCompanyAndApk(scrapy.Item):
    """app如果抓取失败，则存放在另外一张表中
    """
    app_info = scrapy.Field()


class WanDouJiaSpider(scrapy.Spider):

    name = 'wandoujia'
    seed_url = "http://www.wandoujia.com/search?key={app_name}&source=search"

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 404],
    }

    MONGO_URI = "mongodb://localhost:27017/GioCompanyBase"
    MONGO_SUCC_STORE_COLLECTION = "CompanyAndApk"
    MONGO_FAIL_STORE_COLLECTION = "FailCompanyAndApk"

    def start_requests(self):
        mongo_client = MongoUtils(uri=self.MONGO_URI)
        mongo_collection = mongo_client.get_collection('apk_analyse_results')

        for i, doc in enumerate(mongo_collection.find(no_cursor_timeout=True)):
            if not doc.get('app_info'):
                continue
            if doc['app_info'].get('app_name'):
                app_name = doc['app_info'].get('app_name')
                url = self.seed_url.format(app_name=app_name)
                logging.info(' {id} =======> finding {app_name}'.format(id=i, app_name=app_name))
                yield Request(url=url, meta={'app_info': doc['app_info']})

        mongo_client.close()

    def _check_same(self, web_get, app_name):
        web_get = string.lower(web_get).strip()
        app_name = string.lower(app_name).strip()
        if app_name in web_get or web_get in app_name:
            return True
        return False

    def parse(self, response):
        app_name = response.meta['app_info']['app_name']

        soup = BeautifulSoup(response.body, 'html.parser')
        search_item = soup.find('li', attrs={'class': 'search-item'})
        if not search_item:
            logging.warning(' -----> No search_item for {app_name}. url {url}'.
                            format(app_name=app_name, url=response.url))
            return
        link = search_item.find('a', attrs={'class': 'name'})
        if not link:
            logging.warning(' -----> No search_item for {app_name}. url {url}'.
                            format(app_name=app_name, url=response.url))
            return

        if self._check_same(link.get_text(), app_name):
            href = link.get('href')
            if href:
                yield Request(href, meta=response.meta, callback=self.parse_detail, priority=999)
            else:
                logging.warning(' -----> No href for {app_name}. url {url}'.
                                format(app_name=app_name, url=response.url))
        else:
            logging.warning(' -----> This {app_name} not found in wandoujia. find {web_get}'.
                            format(app_name=app_name, web_get=link.get_text()))
            fail_item = FailCompanyAndApk()
            fail_item['app_info'] = response.meta['app_info']
            yield fail_item

    def parse_detail(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        app_name = response.meta['app_info']['app_name']

        item = CompanyAndApk()
        item['wandoujia_link'] = response.url
        item['app_info'] = response.meta['app_info']
        item['com_url'] = ''
        item['com_name'] = ''
        infos = soup.find('dl', attrs={'class': 'infos-list'})
        if infos:
            app_from = infos.find(attrs={'class': 'dev-sites'})
            if app_from:
                item['com_url'] = app_from.get('href', '')
                item['com_name'] = app_from.get_text().strip()
            else:
                logging.warning(' -----> This {app_name} no app_from. url {url}'.
                                format(app_name=app_name, url=response.url))
        else:
            logging.warning(' -----> This {app_name} no infos. url {url}'.
                            format(app_name=app_name, url=response.url))
        yield item





