# -*- coding: utf-8 -*-

import logging
from scrapy.http.response.html import HtmlResponse


class StopDownloadMiddleware(object):

    def __init__(self):
        self.first_warning = True

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        if request.meta.get('fake_url', False):
            if self.first_warning:
                logging.warning("spider donot real crawling, it's just simulation.")
                self.first_warning = False
            return HtmlResponse(request.url)
