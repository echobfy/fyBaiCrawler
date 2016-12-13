# -*- coding: utf-8 -*-

import os
import sys
import json
import zipfile
import logging
import commands
import shutil
import subprocess
reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)


from fyBaiCrawler.utils.excel_utils import ExcelWriter
from fyBaiCrawler.analyse.a25pp.policy import *


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    filename=BASE_DIR + '/logs/25pp/anaylse.log',
    filemode='w'
)


class AppAnaylse(object):
    FILE_NAME_FOR_DOWNLOAD_25PP = os.path.join(BASE_DIR, "datas/25pp/25pp_apps_downloader.txt")
    APPS_DIR = os.path.join(BASE_DIR, "datas/25pp/apps")

    app_column_id_2_name = {
        1: "影音娱乐",
        4: "社交通信",
        2: "系统工具",
        3: "阅读学习",
        6: "摄影美化",
        5: "生活购物",
        7: "出行导航",
        33: "金融理财",
        8: "运动健康",
        9: "商务办公"
    }

    sheet_head = ("Apps", "下载链接", "友盟", "TalkingData", "Mixpanel", "GrowingIO", "神策", "诸葛")

    def __init__(self):
        self.excel_writer = ExcelWriter("records.xls")
        self.column_id_set = set()

        self.anaylse_policies = (FileNameAnaylse(), StringsPolicy())

    def anaylse(self, app_path, app_name, app_downurl, app_ranking, app_column_id):
        unzip_dir = os.path.join(os.getcwd(), app_name.replace("/", "_"))
        status, output = commands.getstatusoutput('unzip -o "{app_path}" -d "{unzip_dir}"'.
                           format(app_path=app_path, unzip_dir=unzip_dir))

        if status != 0:
            logging.warning("app - {app_path} unzip failed. --> {output}".format(app_path=app_path, output=output[0: 200]))
            return unzip_dir

        payload_path = os.path.join(unzip_dir, "Payload")
        if not os.path.exists(payload_path):
            logging.warning("no Payload directory in this app - {app_path}".format(app_path=app_path))
            return unzip_dir

        find_app_command = 'cd "{payload_path}" && ls -d */ | grep "app"'.format(payload_path=payload_path)
        app_dir = commands.getoutput(find_app_command)

        if not app_dir:
            logging.warning("no xxx.app in this app - {app_path}".format(app_path=app_path))
            return unzip_dir

        find_path = os.path.join(payload_path, app_dir)
        anaylse_results = {}
        for anaylse_policy in self.anaylse_policies:
            anaylse_result = anaylse_policy.anaylse(find_path)
            self.combine_anaylse_results(anaylse_results, anaylse_result)

        self.take_notes(app_name, anaylse_results, app_downurl, app_ranking, app_column_id)
        return unzip_dir

    def combine_anaylse_results(self, anaylse_results, anaylse_result):
        """将多次分析结果组合
        :param anaylse_results: 总的分析统计
        :param anaylse_result: 单次的分析结果
        :return:
        """
        for key, value in anaylse_result.items():
            if key in anaylse_results:
                anaylse_results[key] = anaylse_results[key] + ", " + value
            else:
                anaylse_results[key] = anaylse_result[key]

    def anaylse_apps(self):
        def open_file():
            fp = open(self.FILE_NAME_FOR_DOWNLOAD_25PP, "r")
            for line in fp:
                yield json.loads(line)
            fp.close()

        for i, app in enumerate(open_file()):
            logging.info('anaylse number {number} app {app_name} -----------------'.format(number=i, app_name=app['app_name']))
            if not app['files']:
                logging.warning("there is no ipa for this app - {app_name}".format(app_name=app['app_name']))
                continue
            app_path = os.path.join(self.APPS_DIR, app['files'][0]['path'])
            app_name = app['app_name']
            app_downurl = app['app_downurl']
            app_ranking = app['ranking']
            app_column_id = app['column_id']
            unzip_dir = self.anaylse(app_path, app_name, app_downurl, app_ranking, app_column_id)
            if os.path.exists(unzip_dir): shutil.rmtree(unzip_dir)  # 分析完删除该目录

        self.excel_writer.close()

    def take_notes(self, app_name, anaylse_results, app_downurl, app_ranking, app_column_id):
        app_column_name = self.app_column_id_2_name[app_column_id]
        if app_column_id not in self.column_id_set:
            self.column_id_set.add(app_column_id)
            self.excel_writer.write_head(app_column_name, args=self.sheet_head)

        args = [None] * len(self.sheet_head)
        args[0] = app_name
        args[1] = app_downurl
        for company, value in anaylse_results.items():
            index = self.sheet_head.index(company)
            args[index] = value
        self.excel_writer.write_record(app_column_name, requested_index=app_ranking + 1, args=args)


if __name__ == '__main__':
    app_anaylse = AppAnaylse()
    app_anaylse.anaylse_apps()

