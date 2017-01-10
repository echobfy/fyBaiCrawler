# -*- encoding: utf-8 -*-

import os
import sys
import xlwt
import xlrd
import string

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.utils.mongo_utils import MongoUtils


anaylse_company = {
    "友盟": 1,
    "TalkingData": 2,
    "Mixpanel": 3,
    "GrowingIO": 4,
    "神策": 5,
    "诸葛": 6,
    "百度": 7,
    "Google": 8,
    "Flurry": 9,
    "腾讯": 10,
}


class ExcelReader(object):

    def __init__(self, path):
        self.excel = xlrd.open_workbook(path)

    def read_sheets(self):
        for sheet in self.excel.sheets():
            for nrow in range(sheet.nrows):
                yield (sheet.name, nrow - 1, sheet.row_values(nrow))


def split(row):
    results = row.split(',') if row else []
    return map(string.strip, results)


def form(row):
    companies = anaylse_company.copy()
    companies['友盟'] = split(row[2])
    companies['TalkingData'] = split(row[3])
    companies['Mixpanel'] = split(row[4])
    companies['GrowingIO'] = split(row[5])
    companies['神策'] = split(row[6])
    companies['诸葛'] = split(row[7])

    companies['百度'] = []
    companies['Google'] = []
    companies['Flurry'] = []
    companies['腾讯'] = []
    return companies


if __name__ == '__main__':
    excel_read = ExcelReader('/Users/fybai/fyBai-Files/PycharmProjects/fyBaiCrawler/datas/25pp/ipa分析2016-12-13.xls')
    mongo_client = MongoUtils(uri='mongodb://localhost:27017/GioCompanyBase')
    coll = mongo_client.get_collection('ipa_analyse_results')

    for i, (category, rank, row) in enumerate(excel_read.read_sheets()):
        if i == 0 or not row[0]:
            continue

        results = {
            'app_info': {
                'app_name': row[0],
                "category": category,
                "rank": rank,
                "anaylse_result": form(row)
            }
        }
        coll.insert(results, check_keys=False)
        print i

    mongo_client.close()















