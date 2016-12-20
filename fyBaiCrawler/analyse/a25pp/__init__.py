# -*- coding: utf-8 -*-

import os
import json
import shutil
import logging
import threading
from multiprocessing import Queue

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))  # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.utils.excel_utils import ExcelWriter

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    filename=BASE_DIR + '/logs/25pp/anaylse.log',
    filemode='w'
)


class AnaylsePolicy(object):
    def anaylse(self, path):
        raise NotImplemented


class Anaylse(object):
    FILE_NAME = ''
    APPS_DIR = ''
    column_id_2_name = {}

    sheet_head = ("Apps", "下载链接", "友盟", "TalkingData", "Mixpanel", "GrowingIO", "神策", "诸葛")
    excel_writer = ExcelWriter("records.xls")
    column_id_set = set()

    def __init__(self):
        self.anaylse_policies = ()

    def decompression(self, app_path, unzip_dir):
        """根据获得的app路径和需要将其解压缩的路径, 将其解压, 子类实现
        :param app_path:
        :param unzip_dir:
        :return:
        """
        raise NotImplemented

    def go_core_dir(self, unzip_dir):
        """得到解压后的目录, 得到核心目录, 用于后续分析
        :param unzip_dir:
        :return:
        """
        raise NotImplemented

    def clean_directory(self, unzip_dir):
        if os.path.exists(unzip_dir): shutil.rmtree(unzip_dir)  # 分析完删除该目录

    def multi_process_anaylse(self, app_path, unzip_dir, queue, **kwargs):
        status, output = self.decompression(app_path, unzip_dir)  # 1. 解压缩
        if status != 0:
            logging.warning("app - {app_path} decompress failed. --> {output}".
                            format(app_path=app_path, output=output[0: 200]))
            self.clean_directory(unzip_dir)
            queue.put((self, 1, '', kwargs))
            return

        logging.debug('app - {app_path} decompress successfully.'.format(app_path=app_path))

        status, output, core_dir = self.go_core_dir(unzip_dir)  # 2. 进入核心目录
        if status != 0:
            logging.warning("go core dir failed. --> {output}".format(output=output[0: 200]))
            self.clean_directory(unzip_dir)
            queue.put((self, 2, '', kwargs))
            return

        anaylse_results = {}  # 单个app分析结果
        for anaylse_policy in self.anaylse_policies:  # 3. 分析
            anaylse_result = anaylse_policy.anaylse(core_dir)
            self.combine_results(anaylse_results, anaylse_result)
        self.clean_directory(unzip_dir)
        queue.put((self, 0, anaylse_results, kwargs))

    def anaylse_app(self, app_path, app_name, app_downurl, app_ranking, app_column_id, queue):
        raise NotImplemented

    def combine_results(self, anaylse_results, anaylse_result):
        """将分析结果组合
        :param anaylse_results:
        :param anaylse_result:
        :return:
        """
        for key, value in anaylse_result.items():
            if key in anaylse_results:
                anaylse_results[key] = anaylse_results[key] + ", " + value
            else:
                anaylse_results[key] = anaylse_result[key]

    def take_notes(self, app_name, anaylse_results, app_downurl, app_ranking, app_column_id):
        """记录下分析结果
        :param app_name:
        :param anaylse_results:
        :param app_downurl:
        :param app_ranking:
        :param app_column_id:
        :return:
        """
        app_column_name = self.column_id_2_name[app_column_id]
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

    def anaylse(self, processes_pool, queue):
        """分析入口
        :return:
        """

        def open_file():
            fp = open(self.FILE_NAME, "r")
            for line in fp:
                yield json.loads(line)
            fp.close()

        max_i = 0
        for i, app in enumerate(open_file()):
            logging.info(
                'anaylse number {number} app {app_name} -----------------'.format(number=i, app_name=app['app_name']))
            if not app['files']:
                logging.warning("there is no app for this app - {app_name}".format(app_name=app['app_name']))
                continue
            app_path = os.path.join(self.APPS_DIR, app['files'][0]['path'])
            app_name = app['app_name']
            app_downurl = app['app_downurl']
            app_ranking = app['ranking']
            app_column_id = app['column_id']
            self.anaylse_app(app_path, app_name, app_downurl, app_ranking, app_column_id, queue)
            max_i = i

        processes_pool.close()
        return max_i

    def record_results(self, queue, max_i):
        for i in range(0, max_i + 1):
            instance, status, anaylse_results, kwargs = queue.get(True)
            if status != 0:
                continue
            app_name = kwargs.get('app_name')
            app_downurl = kwargs.get('app_downurl')
            app_ranking = kwargs.get('app_ranking')
            app_column_id = kwargs.get('app_column_id')
            instance.take_notes(app_name, anaylse_results, app_downurl, app_ranking, app_column_id)

        self.excel_writer.close()


