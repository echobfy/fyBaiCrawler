# -*- coding: utf-8 -*-
import json
import os
import logging
import base64
import scrapy
from scrapy.http import Request
from scrapy.cmdline import execute

from bs4 import BeautifulSoup
from fyBaiCrawler.items import D25APPItem
from fyBaiCrawler.items import F25APPItem


FILE_NAME_FOR_25PP = "datas/25pp/25pp.txt"
FILE_NAME_FOR_DOWNLOAD_25PP = "datas/25pp/25pp_apps_downloader.txt"


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'f25pp'])


class D25ppSpider(scrapy.Spider):
    """
    抓取25pp网站, 10个类别, 每个类别前5页的app的越狱版的链接
    将下载下来的记录记在在custom_settings中的file_name文件里
    """
    name = "d25pp"

    seed_url = 'http://www.25pp.com/ios/soft/fenlei/3/{column_id}_0_2/{page}'
    start_urls = [
    ]

    custom_settings = {
        "file_name": FILE_NAME_FOR_25PP,

        "LOG_ENABLED": "True",
        "LOG_FILE": "logs/25pp/%s.log" % name,

        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.file_pipeline.FilePipeline': 300,
        }
    }

    column_id = range(1, 10)
    column_id.append(33)

    def start_requests(self):
        for i in self.column_id:
            for j in range(1, 6):
                self.start_urls.append((self.seed_url.format(column_id=i, page=j), i, j))

        for i, (start_url, column_id, page_number) in enumerate(self.start_urls):
            logging.info('{number} -> fetching {url}......'.format(number=i, url=start_url))
            yield Request(start_url, meta={'column_id': column_id, 'page_number':  page_number})

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        records = soup.find_all('a', text="越狱版", attrs={"class": "btn-install-x"})

        for ranking, record in enumerate(records):
            app_downurl = record.get('appdownurl')
            app_name = record.get('appname')

            if not (app_downurl and app_name):
                logging.warning("no appdownurl in {app_name} with {url}!!!!!!".format(app_name=app_name, url=response.url))
                continue

            app_real_downurl = base64.decodestring(app_downurl)

            real_ranking = ranking + (response.meta['page_number'] - 1) * 48  # 每个app的全局排名, 每页app有48个, 在当前页排名为ranking
            item = D25APPItem(app_downurl=app_real_downurl, app_name=app_name,
                              column_id=response.meta['column_id'], ranking=real_ranking)
            yield item


class F25ppSpider(scrapy.Spider):
    """
    根据本文件上面的爬虫抓取下来的app的链接, 去将这些app全部下载下来
    同时将下载结果记录下custom_settings的file_name中, 下载的app文件在FILES_STORE中
    """
    name = "f25pp"

    start_urls = [
        'http://www.i_just_a_fake_spider.com'
    ]

    custom_settings = {
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_DELAY": 1,

        "file_name": FILE_NAME_FOR_DOWNLOAD_25PP,
        "FILES_STORE": 'datas/25pp/apps',

        "DOWNLOAD_TIMEOUT": 180 * 20,  # 放宽到一个小时
        "DOWNLOAD_MAXSIZE": 5 * 1024 * 1024 * 1024,  # 最大可达5G

        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.file_pipeline.FilePipeline': 300,
            'fyBaiCrawler.pipelines.files_downloader_pipeline.FilesDownloaderPipeline': 1,
        }
    }

    def open_25pp(self):
        base_dir = self.settings.get("BASE_DIR")
        apps = []
        fp = open(os.path.join(base_dir, FILE_NAME_FOR_25PP), "r")
        for line in fp:
            apps.append(json.loads(line))
        return apps

    def start_requests(self):
        apps = self.open_25pp()
        for i, app in enumerate(apps):
            logging.info("deal with ------------------- {number} --------------------".format(number=i))
            yield Request(self.start_urls[0], meta={"app": app, 'fake_url': True}, dont_filter=True)  # 声东击西, 请求这个url实际没什么卵用

    def parse(self, response):
        app_name = response.meta['app']['app_name']
        app_downurl = response.meta['app']['app_downurl']
        column_id = response.meta['app']['column_id']
        ranking = response.meta['app']['ranking']

        item = F25APPItem(file_urls=[app_downurl, ], app_name=app_name, app_downurl=app_downurl,
                          column_id=column_id, ranking=ranking)
        yield item





