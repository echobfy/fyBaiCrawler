# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LaGouCompanyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company_url = scrapy.Field()
    company = scrapy.Field()


class D25APPItem(scrapy.Item):
    app_downurl = scrapy.Field()
    app_name = scrapy.Field()

    column_id = scrapy.Field()
    ranking = scrapy.Field()


class F25APPItem(D25APPItem):
    file_urls = scrapy.Field()
    files = scrapy.Field()      # 如果下载失败, 则该files就为空列表[]


