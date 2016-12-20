# -*- coding: utf-8 -*-
import re
import os
from scrapy.cmdline import execute

from a25pp import A25ppSpider, Top25ppSpider, B25ppSpider


class Apk1Spider(A25ppSpider):
    name = 'a_android'

    seed_url = 'http://www.25pp.com/android/soft/fenlei/{column_id}/{page}'
    column_id_2_name = {
        5029: "影音播放",
        5018: "系统工具",
        5014: "通讯社交",
        5024: "手机美化",
        5019: "新闻阅读",
        5016: "摄影图像",
        5026: "考试学习",
        5017: "网上购物",
        5023: "金融理财",
        5020: "生活休闲",
        5021: "旅游出行",
        5028: "健康运动",
        5022: "办公商务",
        5027: "育儿亲子"
    }

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

    def parse(self, response):
        records = self.parse_common(response, attrs={'class': 'btn-install'},
                                    appname=re.compile('.*'), href=re.compile('.*'))
        for ranking, app_name, app_downurl in records:
            real_ranking = ranking + (response.meta['page_number'] - 1) * 48  # 每个app的全局排名, 每页app有48个, 在当前页排名为ranking
            item = self.construct_item(app_downurl, app_name, response.meta['column_id'], real_ranking)
            yield item


class Apk2Spider(B25ppSpider):
    name = 'b_android'

    RESULT_FILE_NAME = os.path.join(Top25ppSpider.RESULT_FILE_DIRECTORY, Apk1Spider.name + ".txt")  # 与Apk1Spider中保存的文件对应
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
        'suffix': '.apk'
    }