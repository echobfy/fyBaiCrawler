# -*- coding: utf-8 -*-

from scrapy.cmdline import execute


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'b_android', "-s", "TEST=True"])
    # execute(['scrapy', 'crawl', 'b_android'])

