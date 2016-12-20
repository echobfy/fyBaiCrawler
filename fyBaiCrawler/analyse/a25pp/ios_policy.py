# -*- coding: utf-8 -*-
import os
import sys
import commands
import logging

from fyBaiCrawler.utils.sys_utils import get_platform_command
from . import AnaylsePolicy


class StringsPolicy(AnaylsePolicy):
    keyword_2_company = {
        "UMTumeng_analytics": "友盟",
        "umeng_report_interval": "友盟",

        "talkingDataTrackEvent": "TalkingData",
        "talkingData": "TalkingData",

        "mixpanel": "Mixpanel",

        "growingio": "GrowingIO",

        "com.sensorsdata": "神策",
        "sensorsdata": "神策",

        "com.zhuge": "诸葛",
        "zhuge": "诸葛",
    }

    def anaylse(self, path):
        companies = {}
        for keyword, company in self.keyword_2_company.items():
            find_str = get_platform_command(
                [
                    'cd "%s" && find . -print| xargs strings | grep "%s"' % (path, keyword),  # for Linux
                    'cd "%s" && find . -print|xargs strings - -arch all |grep "%s"' % (path, keyword),  # for MacOS
                    ''                                                                      # for win32
                 ],
            )
            output = commands.getoutput(find_str)
            if keyword in output:
                logging.info('anaylse {keyword} -> {company} in {path}.'.format(keyword=keyword, company=company, path=path))
                if company in companies: companies[company] = companies[company] + ", " + keyword
                else: companies[company] = keyword
        return companies


class FileNameAnaylse(AnaylsePolicy):
    files_name = {
        "umeng": "友盟",
        "talkingData": "TalkingData",
        "mixpanel": "Mixpanel",
        "growingio": "GrowingIO",
        "sensorsdata": "神策",
        "zhuge": "诸葛",
    }

    def anaylse(self, path):
        companies = {}
        for file_name, company in self.files_name.items():
            framework_name = file_name + '.framework'
            find_str = 'cd "{path}" && find . -print | grep "{framework_name}"'.format(path=path, framework_name=framework_name)

            output = commands.getoutput(find_str)
            if output and framework_name in output:
                logging.info(
                    'anaylse {framework_name} -> {company} in {path}.'.format(framework_name=framework_name, company=company, path=path))
                companies[company] = framework_name
        return companies




