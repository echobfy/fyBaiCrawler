# -*- coding: utf-8 -*-
import json
import logging

import scrapy
from scrapy.http import FormRequest, Request
from fyBaiCrawler.sources.keywords_source import FromMongo
from fyBaiCrawler.items import LaGouCompanyItem


class LaGouSpider(scrapy.Spider, FromMongo):
    name = "lagou"
    start_urls = (
        'https://www.lagou.com/jobs/companyAjax.json?needAddtionalResult=false',
    )

    form_data = {
        "first": "true",
        "pn": "1",
        "kd": "GrowingIO"
    }

    custom_settings = {
        "LOG_FILE": "%s.log" % name
    }

    lagou_company_url = "https://www.lagou.com/gongsi/{company_id}.html"

    def start_requests(self):
        company_list = self.get_doc("ITjuzi")
        for i, company in enumerate(company_list):
            company_name = ""
            if company.get('com_sec_name'):
                company_name = company.get("com_sec_name")
            elif company.get("com_registered_name"):
                company_name = company.get("com_registered_name")
            elif company.get("com_name"):
                company_name = company.get("com_name")
            else:
                logging.info("no company name\n%s" % company)
                continue
            print i
            self.form_data.update(kd=company_name)
            yield FormRequest(self.start_urls[0], formdata=self.form_data, meta={"company": company})

    def parse(self, response):
        result_json = json.loads(response.body)
        company_id = -1
        try:
            company_id = result_json['content']['result'][0]['companyId']
        except:
            logging.error("no company find!!!!!!\n %s" % response.meta['company'])

        if company_id != -1:
            company_url = self.lagou_company_url.format(company_id=company_id)
        else:
            company_url = ""

        item = LaGouCompanyItem()
        item['company_url'] = company_url
        item['company'] = response.meta['company']
        yield item
