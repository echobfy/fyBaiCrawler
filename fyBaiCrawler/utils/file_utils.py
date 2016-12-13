# -*- coding: utf-8 -*-
import os
import json


def is_file_exists(file_path):
    return os.path.exists(file_path)


def fix_file(file_path):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    fp = open(file_path + '25pp_apps_downloader1.txt', "r")
    fp_write = open(file_path + '25pp_apps_downloader.txt', 'w')
    for line in fp:
        app = json.loads(line)
        if app['files']:
            path = app['files'][0]['path']
            if not path.endswith('.ipa'):
                app['files'][0]['path'] += '.ipa'
        fp_write.write(json.dumps(app, ensure_ascii=False) + "\n")

    fp.close()
    fp_write.close()


if __name__ == '__main__':
    fix_file("/Users/bfy/Documents/python/fyBaiCrawler/datas/25pp/")



