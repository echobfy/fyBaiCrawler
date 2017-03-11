# -*- coding: utf-8 -*-

from scrapy.core.downloader.handlers.http10 import HTTP10DownloadHandler


class MyHandler(HTTP10DownloadHandler):

    def download_request(self, request, spider):
        print request.url, request.headers.get('Authorization')
        return super(MyHandler, self).download_request(request, spider)

