# -*- coding: utf-8 -*-

import requests
import scrapy
import logging
import os
from scrapy.pipelines.files import FilesPipeline

from fyBaiCrawler.utils.file_utils import is_file_exists


class FilesDownloaderPipeline(FilesPipeline):

    def __init__(self, store_uri, download_func=None, settings=None):
        super(FilesDownloaderPipeline, self).__init__(store_uri, settings=settings, download_func=download_func)
        self.store_file_path = os.path.join(settings["BASE_DIR"], settings['FILES_STORE'])

    def handle_redirect(self, file_url):
        """
        使用requests包处理重定向, Scrapy暂不支持下载文件重定向
        Scrapy 3.0版本后会解决
        :param file_url:
        :return:
        """
        response = requests.head(file_url)
        if response.status_code == 302 or response.status_code == 301:
            file_url = response.headers["Location"]
        return file_url

    def get_media_requests(self, item, info):
        path = item['app_name'].replace("/", "_") + '.ipa'
        if is_file_exists(os.path.join(self.store_file_path, path)):
            item['files'] = [{'url': item['app_downurl'], 'path': path, 'checksum': ''}]
            logging.debug('{file} already exists, and dont download twice.'.format(file=item['app_name']))
            return
        logging.info('{file} not exist, downloading......'.format(file=item['app_name']))
        redirect_url = self.handle_redirect(item["file_urls"][0])
        yield scrapy.Request(redirect_url, meta={'app_name': item['app_name']})

    def item_completed(self, results, item, info):
        if item.get(self.files_result_field):
            return item
        return super(FilesDownloaderPipeline, self).item_completed(results, item, info)

    def file_path(self, request, response=None, info=None):
        app_name = request.meta['app_name'].replace('/', '_')  # 将文件名中的'/'替换掉
        return "%s%s" % (app_name, ".ipa")


