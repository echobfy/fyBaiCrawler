# -*- coding: utf-8 -*-
from fyBaiCrawler.analyse import AnaylsePolicy


def reverse_map(origin_map):
    result_map = {}
    for key, values in origin_map.items():
        for value in values:
            result_map[value] = key
    return result_map


class WebAnaylsePolicy(AnaylsePolicy):
    """对于Web分析存在两种策略
        1. 执行JS，判断是否有加载了目标站点的JS代码    （优先）
        2. 判断所有文件中的<script>标签中是否出现了关键词
    """
    analysis_helper_web = {
        "友盟": "http://help.cnzz.com/support/kuaisuanzhuangdaima/",
        "诸葛": "http://help.zhugeio.com/hc/kb/article/98401/",
        "神策": "https://www.sensorsdata.cn/manual/js_sdk.html",
        "TalkingData": "http://doc.talkingdata.com/posts/36",
        "腾讯": "http://v2.ta.qq.com/bind/site",
        "Mixpanel": "https://mixpanel.com/help/reference/javascript"
    }

    def anaylse(self, page_data):
        """
        :param page_data: 格式为[{content: ..., url: ...}, .... ]
        :return: 返回{"company1": [x, y, z, ...], "company2": [x, y, z, ...], ......}
        """
        raise NotImplemented


class UrlAnaylsePolicy(WebAnaylsePolicy):
    """根据Response的url判断 ===> 肯定准
    """
    companies_url = {
        "GrowingIO": ["dn-growing.qbox.me"],        # http://www.hunliji.com/
        "百度": ["hm.baidu.com"],                  # http://www.thepaper.cn/
        "Google": [
            "googletagservices.com",            # http://www.hupu.com/
            "google-analytics.com",              # http://bbs.ngacn.cc/
            "googletagmanager.com",             # http://www.xin.com/beijing/
        ],
        "友盟": ["cnzz.com"],                     # http://bbs.ngacn.cc/
        "诸葛": ["zhugeio.com"],                  # http://www.xin.com/beijing/
        "神策": ["sensorsdata.cn", "sensorsdata"],               # http://www.okoer.com/
        "TalkingData": ["talkingdata.com"],
        "腾讯": ["tajs.qq.com"],
        "Mixpanel": ["mixpanel"],
        "Flurry": []
    }

    url_2_company = reverse_map(companies_url)

    def anaylse(self, page_data):
        anaylse_result = {}
        for key, _ in self.companies_url.items():
            anaylse_result[key] = []

        filter = self.url_2_company.keys()
        for page in page_data:
            response = page['response']
            for url in filter:
                if url in response['url']:
                    lst = anaylse_result.setdefault(self.url_2_company[url], [])
                    lst.append(url)
                    filter.remove(url)
        return anaylse_result


class ContentAnaylsePolicy(WebAnaylsePolicy):
    """根据Response的内容判断 ===> 可能准
    因为有些网站在域名上判断不出来，比如acfun使用了神策
    """
    companies_keyword = {
        "GrowingIO": [],
        "百度": [],
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
        "Mixpanel": [],
        "Flurry": []
    }

    keyword_2_company = reverse_map(companies_keyword)

    def anaylse(self, page_data):
        anaylse_result = {}
        for page in page_data:
            response = page['response']
            for keyword in self.keyword_2_company.keys():
                if keyword in response['content']:
                    lst = anaylse_result.setdefault(self.keyword_2_company[keyword], [])
                    lst.append(keyword)
        return anaylse_result



