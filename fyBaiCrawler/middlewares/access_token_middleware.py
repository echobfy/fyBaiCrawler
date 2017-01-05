# -*- coding: utf-8 -*-
import json
import logging
import datetime


class AccessTokenMiddleware(object):

    def __init__(self, settings):
        self.app_id = settings.get("APP_ID")
        self.app_key = settings.get("APP_KEY")
        self.get_access_token_url = settings.get("ACCESS_TOEKN_URL")

        self.access_token = ""
        self.refresh_token = ""
        self.last_refresh = datetime.datetime.now()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def _add_auth(self, request):
        request.headers['Authorization'] = "Bearer " + self.access_token

    def _refresh_token(self, request):
        pass

    def _auth(self, auth_request, origin_request, spider):
        pass


    def process_request(self, request, spider):
        if request.meta.get('no_access_token', False):
            return
        self._add_auth(request)

    def process_response(self, request, response, spider):
        result = json.loads(response.body)

        now = datetime.datetime.now()
        # 1. 认证未过期
        if result.get('code') != 10005:
            return response

        # 2. 认证过期，但access_token存在，且最近一次更新较近，用于处理一些并发请求
        if self.access_token and now - self.last_refresh < datetime.timedelta(minutes=10):
            return self._add_auth(request)

        # 3. 否则开始认证
            # 3.1 当有refresh_token时，直接更新
        if self.refresh_token:
            return self._refresh_token(request)




