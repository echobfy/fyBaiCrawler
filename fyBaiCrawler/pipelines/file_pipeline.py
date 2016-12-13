# -*- coding: utf-8 -*-
import os
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class FilePipeline(object):

    def open_spider(self, spider):
        file_name = spider.settings.get("file_name")
        base_directory = spider.settings.get("BASE_DIR")

        file_path = os.path.join(base_directory, file_name)
        self.fp = open('%s' % file_path, "wr")

    def process_item(self, item, spider):
        doc = {}
        for key, value in item.items():
            doc[key] = value

        json_str = json.dumps(doc, ensure_ascii=False)
        self.fp.write(json_str + '\n')

    def close_spider(self, spider):
        self.fp.close()
