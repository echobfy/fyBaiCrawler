# -*- encoding: utf-8 -*-
import time
import logging

from pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.responsetypes import responsetypes
from scrapy.signalmanager import SignalManager
from twisted.internet import defer, threads

from .shell_process import ShellProcess

# @see https://github.com/flisky/scrapy-phantomjs-downloader/blob/master/scrapy_phantomjs/downloader/handler.py


class PhantomJSDownloadHandler(object):

    def __init__(self, settings):
        base_dir = settings.get('BASE_DIR')
        javascript_file = settings.get('JAVASCRIPT_FILE')
        if not base_dir or not javascript_file:
            raise NotConfigured('BASE_DIR and JAVASCRIPT_FILE, used for find js, must be set in settings.')

        self.cmd = 'phantomjs'
        self.script = '"{base_dir}{javascript_file}"'.format(base_dir=base_dir, javascript_file=javascript_file)

        self.options = settings.get('PHANTOMJS_OPTIONS', [])
        self.wait_for_phantanjs = settings.get('PHATOMJS_SLEEPING', 0)

        max_run = settings.get('PHATOMJS_INSTANCES', 5)
        self.sem = defer.DeferredSemaphore(max_run)
        SignalManager(dispatcher.Any).connect(self._close, signal=signals.spider_closed)

    def download_request(self, request, spider):
        """use semaphore to guard a phantomjs pool"""
        return self.sem.run(self._wait_request, request, spider)

    def _wait_request(self, request, spider):
        logging.debug('New a phantomJs instance...')
        shell_process = ShellProcess(self.cmd, options=self.options, args=[self.script, request.url])
        shell_process.start()

        def callback():
            time.sleep(self.wait_for_phantanjs)
            return shell_process.read()
        dfd = threads.deferToThread(callback)
        dfd.addCallback(self._response, shell_process, request, spider)
        return dfd

    def _response(self, results, shell_process, request, spider):
        returncode, (stdout, stderr) = results
        shell_process.stop()

        url = request.url
        respcls = responsetypes.from_args(url=url, body=stdout)
        if stdout.startswith("Usage"):
            return self.build_response(stdout, respcls, 400, request, spider)
        if stdout.startswith("FAIL"):
            return self.build_response(stdout, respcls, 500, request, spider)
        resp = self.build_response(stdout, respcls, 200, request, spider)
        return defer.succeed(resp)

    def build_response(self, stdout, respcls, status, request, spider):
        if status == 200:
            start1 = stdout.find("HelloWorld")
            start2 = stdout.rfind('{', 0, start1)
            stdout = stdout[start2: ]
        return respcls(url=request.url, status=status, body=stdout, encoding="utf-8")

    def _close(self):
        pass
