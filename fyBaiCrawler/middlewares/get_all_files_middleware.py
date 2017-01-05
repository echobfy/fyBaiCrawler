# -*- coding: utf-8 -*-
import logging
from scrapy.http.response.html import HtmlResponse


class GetAllFilesMiddleware(object):
    """使用PhantomJS获取全部的文件，包括JS，css，html等
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        """在此处劫持request，调用PhantomJS，获取全部的文件返回
        :param request:
        :param spider:
        :return: HTMlResponse 其body表示为[{url: ..., content: ...}, ....]
        """
        if request.meta.get('render_js', False):
            logging.debug(" -------------------> Will render JavaScript --------------------")

            return HtmlResponse(request.url)

