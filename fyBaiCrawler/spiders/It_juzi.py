# -*- coding: utf-8 -*-
import logging
import scrapy
import re
from scrapy.cmdline import execute
from scrapy.http import Request

from bs4 import BeautifulSoup
from fyBaiCrawler.sources.keywords_source import FromMongo

# @see https://www.itjuzi.com/company/24460


if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'itjuzi'])


class ItJuZiCompanyDetailItem(scrapy.Item):

    com_prov = scrapy.Field()               # done 公司位置省

    com_stage_id = scrapy.Field()           # Get 公司规模 ID(1: 初创期, 2:成长发展期, 3:上市公司, 4:成熟期)
    tag = scrapy.Field()                    # Get 公司标签
    com_sec_name = scrapy.Field()           # done 公司简称

    com_status_id = scrapy.Field()          # Get 公司状态 ID (1:运营中, 2:未上线, 3:已关闭, 4:已转型)
    com_city = scrapy.Field()               # done 公司位置市区
    com_born_year = scrapy.Field()          # done 公司创建年

    com_radar_juziindex = scrapy.Field()    # done 桔子指数
    similar_company = scrapy.Field()        # Get 相似公司
    com_cont_email = scrapy.Field()         # None 公司邮箱
    product = scrapy.Field()                # Get 产品
    subcat = scrapy.Field()                 # Get 子行业
    com_logo_archive = scrapy.Field()       # Get 公司缩略图
    com_url = scrapy.Field()                # done 公司网址
    com_born_month = scrapy.Field()         # done 公司创建月
    com_id = scrapy.Field()                 # done 公司 ID
    news = scrapy.Field()                   # Get 新闻
    com_cont_tel = scrapy.Field()           # None 公司电话
    com_des = scrapy.Field()                # done 公司􏰀述信息
    com_video = scrapy.Field()              # done 公司视频
    com_registered_name = scrapy.Field()    # done 公司注册名称
    com_fund_needs_id = scrapy.Field()      # done 公司融资需求 ID (1: 需要融资,2:不需要融资, 3:需求被收购, 4:不明确)
    invest = scrapy.Field()                 # Get 投资
    com_weibo_url = scrapy.Field()          # Get  公司微博
    cat = scrapy.Field()                    # Get 行业
    com_cont_addr = scrapy.Field()          # None 公司详细地址
    team = scrapy.Field()                   # Get 团队
    com_logo = scrapy.Field()               # done 公司 LOGO
    com_weixin_id = scrapy.Field()          # Get  公司微信
    com_name = scrapy.Field()               # done 公司名称


class ItJuZiSpider(scrapy.Spider):
    name = "itjuzi"

    seed_url = "http://www.itjuzi.com/company/{company_id}"
    start_urls = []

    MONGO_DB = "GIO"
    MONGO_COLLECTION = "company_detail"

    custom_settings = {
        "ITEM_PIPELINES": {
            'fyBaiCrawler.pipelines.mongo_pipeline.MongoPipeline': 300,
        },
        "DOWNLOAD_DELAY": 3,
    }

    def start_requests(self):
        keywords_source = FromMongo()
        company_list = keywords_source.get_doc("GIO", "ITjuzi")
        for i, company in enumerate(company_list):
            if company.get("com_id"):
                url = self.seed_url.format(company_id=company["com_id"])
                yield Request(url, meta={"company": company})
                logging.debug('request for {com_id} - {company_name} -------- {number} -------'.
                             format(com_id=company["com_id"], company_name=company['com_name'], number=i))
            else:
                logging.warning("no com_id in {company}.".format(company=company))
        keywords_source.close()

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        item = ItJuZiCompanyDetailItem()

        self.parse_company(response.meta['company'], item)
        item['tag'] = []
        self.parse_tags(soup, item)

        item['com_status_id'] = 1
        self.parse_com_status_id(soup, item)

        item['similar_company'] = []
        self.parse_similar_company(soup, item)

        item['news'] = []
        self.parse_news(soup, item)

        item['product'] = []
        self.parse_products(soup, item)

        item['com_logo_archive'] = ''
        self.parse_com_logo_archive(soup, item)

        item['com_weixin_id'] = ''
        self.parse_com_weixin_id(soup, item)

        item['com_weibo_url'] = ''
        self.parse_com_weibo_url(soup, item)

        item['invest'] = []
        self.parse_invest(soup, item)

        item['team'] = []
        self.parse_team(soup, item)

        item['cat'] = {}
        self.parse_cat(soup, item)

        item['subcat'] = {}
        self.parse_subcat(soup, item)

        item['com_stage_id'] = ''
        self.parse_com_stage_id(soup, item)

        yield item

    def parse_company(self, company, item):
        item['com_prov'] = company.get('com_prov', "")
        item['com_sec_name'] = company.get('com_sec_name', "")
        item['com_city'] = company.get('com_city', "")
        item['com_born_year'] = company.get('com_born_year', -1)
        item['com_radar_juziindex'] = company.get('com_radar_juziindex', -1)
        item['com_url'] = company.get('com_url', "")
        item['com_born_month'] = company.get('com_born_month', -1)
        item['com_id'] = company.get('com_id', -1)
        item['com_des'] = company.get('com_des', "")
        item['com_video'] = company.get('com_video', "")
        item['com_registered_name'] = company.get('com_registered_name', "")
        item['com_fund_needs_id'] = company.get('com_fund_needs_id', -1)
        item['com_logo'] = company.get('com_logo', "")
        item['com_name'] = company.get('com_name', "")

        # ------------ 字段不存在 ------------------
        item['com_cont_addr'] = ''
        item['com_cont_tel'] = ''
        item['com_cont_email'] = ''

    def parse_com_status_id(self, soup, item):
        com_status_id = soup.find("select", attrs={"id": "select", "name": "com_status_id"})
        selected = com_status_id.find("option", attrs={"selected": "selected"})
        value = selected['value']
        item['com_status_id'] = value

    def parse_tags(self, soup, item):
        tags = soup.find_all("a", href=re.compile("tag/\d+"))
        for tag in tags:
            tag_doc = {}
            tag_name = tag.get_text()
            tag_doc["tag_name"] = tag_name

            search = re.search("tag/(\d+)", tag['href'])
            tag_doc["tag_id"] = search.group(1) if search else -1
            item['tag'].append(tag_doc)

    def parse_similar_company(self, soup, item):
        similar_companies = soup.find_all("a", href=re.compile("company/\d+"))
        for similar_company in similar_companies:
            if not (similar_company.find('left') and similar_company.find('right')):
                continue
            doc = {}
            doc['com_logo'] = similar_company.find('left').find('img', recursive=True)['src']
            doc['com_name'] = similar_company.find('right').get_text()
            serach = re.search("company/(\d+)", similar_company['href'])
            doc['com_id'] = serach.group(1) if serach else -1
            item['similar_company'].append('doc')

    def parse_products(self, soup, item):
        list_product_tag = soup.find('ul', attrs={"class": "list-prod"})
        if not list_product_tag:
            return
        products = list_product_tag.find_all('li', attrs={'class': 'ugc-block-item'})

        for product in products:
            com_pro_type_name = com_pro_name = com_pro_detail = com_pro_id = com_pro_type_id = ''

            doc = {}
            h4_tag = product.find('h4')
            if h4_tag:
                tag_tag = h4_tag.find('span', attrs={'class': 'tag'})
                if tag_tag: com_pro_type_name = tag_tag.get_text()

                name_tag = h4_tag.find('b')
                if name_tag: com_pro_name = name_tag.get_text()

            com_pro_detail = product.find('p').get_text() if product.find('p') else ''
            com_pro_id_tag = product.find('input', attrs={'name': 'prod_id'})
            if com_pro_id_tag and com_pro_id_tag.get('value'): com_pro_id = com_pro_id_tag['value']

            doc['com_pro_type_name'] = com_pro_type_name
            doc['com_pro_id'] = com_pro_id
            doc['com_pro_detail'] = com_pro_detail
            doc['com_pro_name'] = com_pro_name.strip()
            doc['com_pro_type_id'] = com_pro_type_id

            item['product'].append(doc)

    def parse_com_logo_archive(self, soup, item):
        com_logo_archive_tag = soup.find('input', attrs={'name': 'com_logo_archive'})
        if not com_logo_archive_tag: return
        parent = com_logo_archive_tag.parent
        img_tag = parent.find('img', src=re.compile('http.*'))
        if img_tag:
            item['com_logo_archive'] = img_tag['src']

    def parse_com_weixin_id(self, soup, item):
        weixin_tag = soup.find('a', attrs={'class': 'link-weixin'})
        if weixin_tag and weixin_tag.get('href'):
            item['com_weixin_id'] = weixin_tag.get('href')

    def parse_com_weibo_url(self, soup, item):
        weibo_tag = soup.find('a', attrs={'class': 'link-weibo'})
        if weibo_tag and weibo_tag.get('href'):
            item['com_weibo_url'] = weibo_tag.get('href')

    def parse_invest(self, soup, item):
        invests = soup.find('table', attrs={'class': 'list-round-v2'})
        if not invests: return

        invest_list = []
        for invest in invests.find_all('tr'):
            doc = {}
            tds = invest.find_all('td')
            doc['date'] = tds[0].find('span', attrs={'class': 'date c-gray'}).get_text()
            doc['round'] = tds[1].find('span', attrs={'class': 'round'}).get_text()
            doc['finades'] = tds[2].find('span', attrs={'class': 'finades'}).get_text()

            firms = []
            for firm in tds[3].find_all('a', href=re.compile('investfirm/\d+')):
                invest_firm_id = re.search('investfirm/(\d+)', firm['href']).group(1)
                firms.append({'investfirm': firm.get_text(), 'invest_firm_id': invest_firm_id})
            doc['investfirm'] = firms

            invest_list.append(doc)
        item['invest'] = invest_list

    def parse_news(self, soup, item):
        news_tag = soup.find('ul', attrs={'class': 'list-news'})
        if not news_tag: return

        news = news_tag.find_all('li', attrs={'class': 'ugc-block-item'})
        news_list = []
        for new in news:
            doc = {}
            news_title = new.find('p', attrs={'class': 'title'})
            if not news_title: continue

            news_title = news_title.find('a', href=re.compile("http.*"))
            if not news_title: continue

            doc['com_new_url'] = news_title.get('href')
            doc['com_new_name'] = news_title.get_text().strip()

            new_type = new.find('span', attrs={'class': 'tag'})
            doc['com_new_type_name'] = new_type.get_text() if new_type else ''

            time = new.find('span', attrs={'class': 't-small c-gray marr10'})
            doc['com_new_year'] = time.get_text().split(".")[0] if time else ''
            doc['com_new_month'] = time.get_text().split(".")[1] if time else ''
            doc['com_new_day'] = time.get_text().split(".")[2] if time else ''

            news_list.append(doc)
        item['news'] = news_list

    def parse_team(self, soup, item):
        team_big_tag = soup.find('ul', attrs={'class': 'list-prodcase'})
        if not team_big_tag: return

        teams = team_big_tag.find_all('li')
        team_list = []
        for team in teams:
            doc = {}

            person = team.find('a', attrs={'class': 'title'}, href=re.compile("person/\d+"))

            doc['per_name'] = person.find('span', attrs={'class': 'c'}).get_text()
            doc['position'] = person.find('span', attrs={'class': 'c-gray'}).get_text()
            doc['per_id'] = re.search("person/(\d+)", person['href']).group(1)

            team_list.append(doc)
        item['team'] = team_list

    def parse_cat(self, soup, item):
        scope = soup.find('span', attrs={'class': 'scope c-gray-aset'})
        cat = scope.find('a', href=re.compile('scope=\d+'))
        if cat:
            doc = {'cat_id': re.search('scope=(\d+)', cat['href']).group(1), 'cat_name': cat.get_text()}
            item['cat'] = doc

    def parse_subcat(self, soup, item):
        scope = soup.find('span', attrs={'class': 'scope c-gray-aset'})
        sub_cat = scope.find('a', href=re.compile('sub_scope=\d+'))
        if sub_cat:
            doc = {'cat_id': re.search('sub_scope=(\d+)', sub_cat['href']).group(1), 'cat_name': sub_cat.get_text()}
            item['subcat'] = doc

    def parse_com_stage_id(self, soup, item):
        com_infos = soup.find('div', attrs={'class': 'block-inc-info'})
        if not com_infos: return
        des_more = com_infos.find('div', attrs={'class': 'des-more'})
        if not des_more: return

        des_more_text = des_more.get_text()
        ans = re.search(u'公司规模：(.*)人', des_more_text, re.M)
        if ans:
            item['com_stage_id'] = ans.group(1)


