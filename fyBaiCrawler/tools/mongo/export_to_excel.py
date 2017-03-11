# -*- encoding: utf-8 -*-

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.utils.mongo_utils import MongoUtils
from fyBaiCrawler.utils.excel_utils import ExcelWriter


class ExportToMongo(object):

    def __init__(self, uri):
        self.mongo_client = MongoUtils(uri)
        self.excel_writer = ExcelWriter("data.xls")
        self.heads = ('公司', '链接', '公司注册名称', '规模', '子行业', '最后一次融资轮次', '最后一次融资金额', '公司阶段')
        self.status_map = {
            '1': '运营中',
            '2': '未上线',
            '3': '已关闭',
            '4': '已转型'
        }
        self.link = 'http://www.itjuzi.com/company/'

    def export(self):
        cat_set = set()
        for i, doc in enumerate(self.mongo_client.get_collection("company_detail").find()):
            print i, doc['com_id']
            cat = doc['cat'].get('cat_name')
            if not cat:
                continue
            if cat not in cat_set:
                cat_set.add(cat)
                self.excel_writer.write_head(sheet_name=cat, args=self.heads)

            invest = ''
            invest_money = ''
            if doc['invest']:
                invest = doc['invest'][0]['round']
                invest_money = doc['invest'][0]['finades']

            self.excel_writer.write_record(sheet_name=cat, args=(
                doc['com_name'],
                self.link + doc['com_id'],
                doc['com_registered_name'],
                doc['com_stage_id'],
                doc['subcat'].get('cat_name', ''),
                invest,
                invest_money,
                self.status_map.get(doc['com_status_id'], '未知')
            ))

    def close(self):
        self.mongo_client.close()
        self.excel_writer.close()


if __name__ == '__main__':
    export = ExportToMongo(uri='mongodb://localhost:27017/itjuzi')
    export.export()
    export.close()