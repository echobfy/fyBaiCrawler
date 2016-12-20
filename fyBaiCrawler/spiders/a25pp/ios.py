# -*- coding: utf-8 -*-
import re
import os
import base64
from scrapy.cmdline import execute

from a25pp import A25ppSpider, Top25ppSpider, B25ppSpider


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'android'])


class Ipa1SPider(A25ppSpider):
    name = 'a_ios'

    seed_url = 'http://www.25pp.com/ios/soft/fenlei/3/{column_id}_0_2/{page}'
    column_id_2_name = {
        1: "影音娱乐",
        4: "社交通信",
        2: "系统工具",
        3: "阅读学习",
        6: "摄影美化",
        5: "生活购物",
        7: "出行导航",
        33: "金融理财",
        8: "运动健康",
        9: "商务办公"
    }

    RESULT_FILE_NAME = os.path.join(Top25ppSpider.RESULT_FILE_DIRECTORY, name + ".txt")      # TODO: 如何更优美访问父类静态变量
    LOGS_FILE_NAME = os.path.join(Top25ppSpider.LOGS_FILE_DIRECTORY, name + ".log")

    custom_settings = {
        "file_name": RESULT_FILE_NAME,

        "LOG_ENABLED": "True",
        "LOG_FILE": LOGS_FILE_NAME,

        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.file_pipeline.FilePipeline': 300,
        }
    }

    def parse(self, response):
        records = self.parse_common(response, attrs={"class": "btn-install-x"}, text='越狱版')
        for ranking, app_name, app_downurl in records:
            app_real_downurl = base64.decodestring(app_downurl)
            real_ranking = ranking + (response.meta['page_number'] - 1) * 48  # 每个app的全局排名, 每页app有48个, 在当前页排名为ranking
            item = self.construct_item(app_real_downurl, app_name, response.meta['column_id'], real_ranking)
            yield item


class Ipa2Spider(B25ppSpider):
    name = 'b_ios'

    RESULT_FILE_NAME = os.path.join(Top25ppSpider.RESULT_FILE_DIRECTORY, Ipa1SPider.name + ".txt")  # 与Apk1Spider中保存的文件对应
    LOGS_FILE_NAME = os.path.join(Top25ppSpider.LOGS_FILE_DIRECTORY, name + ".log")
    DOWNLOAD_FILE_NAME = os.path.join(Top25ppSpider.RESULT_FILE_DIRECTORY, name + ".txt")
    APPS_STORE_PATH = os.path.join(Top25ppSpider.APP_STORE_DIRECTORY, name)

    custom_settings = {
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_DELAY": 1,

        "file_name": DOWNLOAD_FILE_NAME,
        "FILES_STORE": APPS_STORE_PATH,

        "DOWNLOAD_TIMEOUT": 180 * 20,  # 放宽到一个小时
        "DOWNLOAD_MAXSIZE": 5 * 1024 * 1024 * 1024,  # 最大可达5G

        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.file_pipeline.FilePipeline': 300,
            'fyBaiCrawler.pipelines.files_downloader_pipeline.FilesDownloaderPipeline': 1,
        },
        'suffix': '.ipa'
    }