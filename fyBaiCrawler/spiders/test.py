# -*- coding: utf-8 -*-
import json
import time
import logging

import scrapy
from scrapy.http import FormRequest, Request
from scrapy.cmdline import execute
from fyBaiCrawler.sources.keywords_source import FromMongo


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'test'])


class LaGouSpider(scrapy.Spider, FromMongo):
    name = "test"
    start_urls = (
        'http://www.cc98.org/',
    )

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 50,
        "CONCURRENT_REQUESTS_PER_IP": 50,
        "CONCURRENT_REQUESTS": 50

    }

    def start_requests(self):
        self.start = time.time()
        for i in range(0, 100):
            yield Request(self.start_urls[0], dont_filter=True)

    def parse(self, response):
        pass

    def closed(self, reason):
        end = time.time()
        print end - self.start






