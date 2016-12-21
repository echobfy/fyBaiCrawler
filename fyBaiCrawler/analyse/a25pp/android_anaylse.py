# -*- coding: utf-8 -*-

import os
import sys
import commands
import logging
import multiprocessing

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from fyBaiCrawler.analyse.a25pp import Anaylse, BASE_DIR
from fyBaiCrawler.spiders.a25pp.android import Apk2Spider, Apk1Spider
from fyBaiCrawler.analyse.a25pp.android_policy import FileNamePolicy


def agent(cls_instance, *args, **kwargs):
    return cls_instance.multi_process_anaylse(*args, **kwargs)


# def agent_callback(results):
#     cls_instance, status, anaylse_result, kwargs = results
#     cls_instance.process_anaylse_result(status, anaylse_result, kwargs)


class AndroidAnaylse(Anaylse):
    FILE_NAME = os.path.join(BASE_DIR, Apk2Spider.DOWNLOAD_FILE_NAME)
    APPS_DIR = os.path.join(BASE_DIR, Apk2Spider.APPS_STORE_PATH)

    column_id_2_name = Apk1Spider.column_id_2_name

    sheet_head = ("Apps", "下载链接", "GrowingIO", "百度", "友盟", "Google", "诸葛", "神策", "TalkingData", "腾讯", "Flurry", "Mixpanel")

    def __init__(self):
        super(AndroidAnaylse, self).__init__()
        self.anaylse_policies = (FileNamePolicy(), )      # 分析策略

    def decompression(self, app_path, unzip_dir):
        status, output = commands.getstatusoutput('d2j-dex2smali.sh "{app_path}" -o "{unzip_dir}"'.format(
            app_path=app_path, unzip_dir=unzip_dir
        ))
        return status, output

    def go_core_dir(self, unzip_dir):
        return 0, '', unzip_dir

    def anaylse_app(self, app_path, app_name, app_downurl, app_ranking, app_column_id, queue):
        unzip_dir = os.path.join(os.getcwd(), app_name.replace("/", "_"))

        result = processes_pool.apply_async(
            agent,
            args=(self, app_path, unzip_dir, queue),
            kwds={
                "app_name": app_name,
                "app_downurl": app_downurl,
                "app_ranking": app_ranking,
                "app_column_id": app_column_id
            },
            # callback=agent_callback,
        )


if __name__ == '__main__':
    anaylse = AndroidAnaylse()

    cores = multiprocessing.cpu_count() * 2
    logging.info(' ---> start {cores} processes in pool.'.format(cores=cores))
    processes_pool = multiprocessing.Pool(processes=cores)

    manager = multiprocessing.Manager()
    queue = manager.Queue()

    try:
        max_i = anaylse.anaylse(processes_pool, queue)
        anaylse.record_results(queue, max_i)
    except Exception, e:
        import traceback
        traceback.print_exc()
        processes_pool.close()
        processes_pool.terminate()



