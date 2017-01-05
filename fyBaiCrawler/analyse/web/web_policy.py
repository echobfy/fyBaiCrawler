# -*- coding: utf-8 -*-
from fyBaiCrawler.analyse import AnaylsePolicy


class WebAnaylsePolicy(AnaylsePolicy):
    """对于Web分析存在两种策略
        1. 执行JS，判断是否有加载了目标站点的JS代码    （优先）
        2. 判断所有文件中的<script>标签中是否出现了关键词
    """
    analysis_helper_web = {
        "友盟": "http://help.cnzz.com/support/kuaisuanzhuangdaima/",
        "诸葛IO": "http://help.zhugeio.com/hc/kb/article/98401/",
        "神策": "https://www.sensorsdata.cn/manual/js_sdk.html",
        "TalkingData": "http://doc.talkingdata.com/posts/36",
        "腾讯": "http://v2.ta.qq.com/bind/site",
        "mixpanel": "https://mixpanel.com/help/reference/javascript"
    }

    def anaylse(self, page_data):
        raise NotImplemented


class UrlAnaylsePolicy(WebAnaylsePolicy):
    """根据Response的url判断 ===> 肯定准
    """
    companies_url = {
        "GrowingIO": ["dn-growing.qbox.me"],        # http://www.hunliji.com/
        "Baidu": ["hm.baidu.com"],                  # http://www.thepaper.cn/
        "Google": [
            "googletagservices.com",            # http://www.hupu.com/
            "google-analytics.com",              # http://bbs.ngacn.cc/
            "googletagmanager.com",             # http://www.xin.com/beijing/
        ],
        "友盟": ["cnzz.com"],                     # http://bbs.ngacn.cc/
        "诸葛": ["zhugeio.com"],                  # http://www.xin.com/beijing/
        "神策": ["sensorsdata.cn"],               # http://www.okoer.com/
        "TalkingData": ["talkingdata.com"],
        "腾讯": ["tajs.qq.com"],
        "mixpanel": []
    }

    def anaylse(self, page_data):
        pass


class ContentAnaylsePolicy(WebAnaylsePolicy):
    """根据Response的内容判断 ===> 可能准
    因为有些网站在域名上判断不出来，比如acfun使用了神策
    """
    companies_keyword = {
        "GrowingIO": [],
        "Baidu": [],
        "Google": [],
        "友盟": [],
        "诸葛": [],
        "神策": [
            "sensorsDataAnalytic",
            "sensorsdata-event",     # http://www.acfun.cn/
            "sensorsdata",
        ],
        "TalkingData": [],
        "腾讯": [],
        "mixpanel": []
    }

    def anaylse(self, page_data):
        pass



