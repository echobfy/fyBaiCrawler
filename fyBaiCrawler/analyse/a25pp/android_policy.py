# -*- coding: utf-8 -*-
import os
import logging

from fyBaiCrawler.analyse.a25pp import AnaylsePolicy


class FileNamePolicy(AnaylsePolicy):
    file_name_2_companies = {
        "com/growingio/android/sdk/collection/GrowingIO.smali": "GrowingIO",
        "com/baidu/mobstat/StatService.smali": "百度",
        "com/umeng/analytics/MobclickAgent.smali": "友盟",
        "com/google/android/gms/analytics/GoogleAnalytics.smali ": "Google",
        "com/zhuge/analysis/stat/ZhugeSDK.smali": "诸葛",
        "com/sensorsdata/analytics/android/sdk/SensorsDataAPI.smali": "神策",
        "com/talkingdata/sdk/TalkingDataSDK.smali": "TalkingData",
        "com/tencent/mid/api/MidService.smali": "腾讯",
        "com/flurry/android/FlurryAgent.smali": "Flurry",
        "com/mixpanel/android/mpmetrics/MixpanelAPI.smali": "Mixpanel"
    }

    def anaylse(self, path):
        anaylse_results = {}
        for file_name, company in self.file_name_2_companies.items():
            if os.path.exists(os.path.join(path, file_name)):
                anaylse_results[company] = file_name[file_name.rfind('/') + 1:]
        logging.info('------------ {anaylse_results} -------'.format(anaylse_results=str(anaylse_results)))
        return anaylse_results

