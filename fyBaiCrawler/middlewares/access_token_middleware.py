# -*- coding: utf-8 -*-

"""
This is a download middleware for getting and refreshing the access token to targeted web site.

To activate it you must configure you APP_ID, APP_KEY, ACCESS_TOKEN_URL,
EXPIRE_IN_SECOND to targeted web site.
"""

import sys
import json
import logging
import datetime

from twisted.internet.defer import Deferred, maybeDeferred
from scrapy.http import FormRequest
from scrapy.utils.log import failure_to_exc_info
from scrapy.exceptions import NotConfigured, CloseSpider, IgnoreRequest
from scrapy.downloadermiddlewares.robotstxt import RobotsTxtMiddleware


logger = logging.getLogger(__name__)


class TokenAttribute(object):
    def __init__(self, access_token, refresh_token, last_refresh):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.last_refresh = last_refresh


class AccessTokenMiddleware(object):
    ADVANCED_EXPIRE_TIMEDELTA = 15 * 60     # 15 minutes
    DOWNLOAD_PRIORITY = RobotsTxtMiddleware.DOWNLOAD_PRIORITY

    def __init__(self, crawler):
        self.crawler = crawler
        self.app_id = crawler.settings.get("APP_ID")
        self.app_key = crawler.settings.get("APP_KEY")
        self.access_token_url = crawler.settings.get("ACCESS_TOEKN_URL")

        advanced_expire_in_seconds = crawler.settings.getint(       # should refresh access token in advance
            "ADVANCED_EXPIRE_IN_SECOND", self.ADVANCED_EXPIRE_TIMEDELTA)
        self.advanced_expire_timedelta = datetime.timedelta(seconds=advanced_expire_in_seconds)
        self.expire_timedelta = datetime.timedelta(seconds=crawler.settings.getint("EXPIRE_IN_SECOND")) - \
                                self.advanced_expire_timedelta

        if not (self.app_id and self.app_key and self.access_token_url):
            raise NotConfigured

        self._token_map = {}
        self._token_seq = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if request.meta.get('dont_need_access_token'):
            return
        d = maybeDeferred(self.refreshing_token, request, spider)
        d.addCallback(self.add_auth, request, spider)
        return d

    def _next_token_seq(self):
        self._token_seq += 1
        return self._token_seq

    def _is_first_token_seq(self):
        return self._token_seq == 1

    def refreshing_token(self, request, spider):
        now_token_seq = self._token_seq

        if now_token_seq not in self._token_map or self._is_access_token_expired(now_token_seq):
            now_token_seq = self._next_token_seq()
            self._token_map[now_token_seq] = Deferred()

            if now_token_seq - 2 in self._token_map:
                del self._token_map[now_token_seq - 2]

            token_request = self._token_request()
            dfd = self.crawler.engine.download(token_request, spider)
            dfd.addCallback(self._parse_access_token, now_token_seq)
            dfd.addErrback(self._logerror, token_request, spider)
            dfd.addErrback(self._get_access_token_error, now_token_seq)

        if isinstance(self._token_map[now_token_seq], Deferred):
            d = Deferred()

            def cb(result):
                d.callback(result)
                return result
            self._token_map[now_token_seq].addCallback(cb)
            return d
        else:
            return self._token_map[now_token_seq]

    def _parse_access_token(self, response, token_seq):
        body = json.loads(response.text)
        if body['code'] != 1000:
            raise GetAccessTokenFailure(body)
        access_token = body['data']['access_token']
        refresh_token = body['data']['refresh_token']
        last_refresh = datetime.datetime.now()

        dfd = self._token_map[token_seq]
        ta = TokenAttribute(access_token, refresh_token, last_refresh)
        self._token_map[token_seq] = ta
        dfd.callback(ta)

    def _token_request(self):
        formdata = {
            'appid': self.app_id,
            'appkey': self.app_key,
        }
        token_request = FormRequest(
            url=self.access_token_url,
            meta={'dont_need_access_token': True},
        )

        new_formdata = formdata.copy()          # TODO refresh_token更新不成功，先直接不refresh，再获取access_token
        # if self._is_first_token_seq():
        #     new_formdata.update({'granttype': 'client_credentials'})
        # else:
        #     ta = self._token_map[self._token_seq - 1]
        #     new_formdata.update({'granttype': 'refresh_token', 'refresh_token': ta.refresh_token})
        new_formdata.update({'granttype': 'client_credentials'})
        return token_request.replace(formdata=new_formdata)

    def add_auth(self, ta, request, spider):
        if not ta or not ta.access_token:
            logger.error("Forbidden by AccessToken: %(request)s",
                         {'request': request}, extra={'spider': spider})
            raise CloseSpider
        request.headers['Authorization'] = "Bearer " + ta.access_token

    def _is_access_token_expired(self, now_token_seq):
        ta = self._token_map[now_token_seq]
        last_refresh = ta.last_refresh if isinstance(ta, TokenAttribute) else None
        now = datetime.datetime.now()

        if last_refresh and now - last_refresh > self.expire_timedelta:
            return True
        return False

    def _logerror(self, failure, request, spider):
        if failure.type is not IgnoreRequest:
            logger.error("Error downloading %(request)s: %(f_exception)s",
                         {'request': request, 'f_exception': failure.value},
                         exc_info=failure_to_exc_info(failure),
                         extra={'spider': spider})
        else:
            logger.error("Get Access Token request %(request)s should not be Ignore.",
                         {'request': request}, exc_info=failure_to_exc_info(failure),
                         extra={'spider': spider})
        return failure

    def _get_access_token_error(self, failure, token_seq):
        dfd = self._token_map[token_seq]
        self._token_map[token_seq] = None
        dfd.callback(None)


class GetAccessTokenFailure(Exception):

    def __init__(self, response):
        super(GetAccessTokenFailure, self).__init__()
        self.status = response

    def __str__(self):
        return json.dumps(self.status)






