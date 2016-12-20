# -*- coding: utf-8 -*-
import json
import os
import logging
import scrapy
from scrapy.http import Request

from bs4 import BeautifulSoup
from fyBaiCrawler.items import D25APPItem
from fyBaiCrawler.items import F25APPItem


class Top25ppSpider(scrapy.Spider):
    name = ''

    RESULT_FILE_DIRECTORY = 'datas/25pp'
    LOGS_FILE_DIRECTORY = 'logs/25pp'
    APP_STORE_DIRECTORY = 'datas/25pp/apps'


class A25ppSpider(Top25ppSpider):
    """
    抓取25pp网站, 10个类别, 每个类别前5页的app的越狱版的链接
    将下载下来的记录记在在custom_settings中的file_name文件里
    """
    name = ''
    seed_url = ''
    column_id_2_name = {}

    FETCH_PAGE = range(1, 6)

    RESULT_FILE_NAME = os.path.join(Top25ppSpider.RESULT_FILE_DIRECTORY, name + ".txt")
    LOGS_FILE_NAME = os.path.join(Top25ppSpider.LOGS_FILE_DIRECTORY, name + ".log")

    custom_settings = {
        "file_name": RESULT_FILE_NAME,

        "LOG_ENABLED": "True",
        "LOG_FILE": LOGS_FILE_NAME,

        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.file_pipeline.FilePipeline': 300,
        }
    }

    def construct_start_urls(self):
        for i in self.column_id_2_name.keys():
            for j in self.FETCH_PAGE:
                self.start_urls.append((self.seed_url.format(column_id=i, page=j), i, j))

    def start_requests(self):
        self.construct_start_urls()
        for i, (start_url, column_id, page_number) in enumerate(self.start_urls):
            logging.info('{number} -> fetching {url}......'.format(number=i, url=start_url))
            yield Request(start_url, meta={'column_id': column_id, 'page_number':  page_number})
            if self.settings.get('TEST', False):
                break

    def parse(self, response):
        raise NotImplemented

    def parse_common(self, response, attrs={}, **kwargs):
        soup = BeautifulSoup(response.text, "html.parser")
        records = soup.find_all('a', attrs=attrs, **kwargs)

        for ranking, record in enumerate(records):
            app_downurl = record.get('appdownurl')
            app_name = record.get('appname')

            if not (app_downurl and app_name):
                logging.warning(
                    "no appdownurl in {app_name} with {url}!!!!!!".format(app_name=app_name, url=response.url))
                continue
            yield (ranking, app_name, app_downurl)

    def construct_item(self, app_downurl, app_name, column_id, ranking):
        item = D25APPItem(app_downurl=app_downurl, app_name=app_name,
                          column_id=column_id, ranking=ranking)
        return item


class B25ppSpider(scrapy.Spider):
    """
    根据本文件上面的爬虫抓取下来的app的链接, 去将这些app全部下载下来
    同时将下载结果记录下custom_settings的file_name中, 下载的app文件在FILES_STORE中
    """
    name = ''

    start_urls = [
        'http://www.i_just_a_fake_spider.com'
    ]

    RESULT_FILE_NAME = ''

    def open_25pp(self):
        base_dir = self.settings.get("BASE_DIR")
        apps = []
        fp = open(os.path.join(base_dir, self.RESULT_FILE_NAME), "r")
        for line in fp:
            apps.append(json.loads(line))
        return apps

    def start_requests(self):
        apps = self.open_25pp()
        for i, app in enumerate(apps):
            logging.info("deal with ------------------- {number} --------------------".format(number=i))
            yield Request(self.start_urls[0], meta={"app": app, 'fake_url': True}, dont_filter=True)  # 声东击西, 请求这个url实际没什么卵用
            if self.settings.get('TEST', False):
                break

    def parse(self, response):
        app_name = response.meta['app']['app_name']
        app_downurl = response.meta['app']['app_downurl']
        column_id = response.meta['app']['column_id']
        ranking = response.meta['app']['ranking']

        item = F25APPItem(file_urls=[app_downurl, ], app_name=app_name, app_downurl=app_downurl,
                          column_id=column_id, ranking=ranking)
        yield item





