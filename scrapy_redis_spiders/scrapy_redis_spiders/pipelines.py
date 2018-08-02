# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.web.client import Agent, getPage, ResponseDone, PotentialDataLoss

from twisted.internet import defer, reactor, protocol
from twisted.web._newclient import Response
from io import BytesIO


class ScrapyRedisSpidersPipeline(object):
    def process_item(self, item, spider):
        return item


class _ResponseReader(protocol.Protocol):
     #与BigfilePipeline配套下载大文件

    def __init__(self, finished, txresponse, file_name):
        self._finished = finished
        self._txresponse = txresponse
        self._bytes_received = 0
        self.f = open(file_name, mode='wb')

    def dataReceived(self, bodyBytes):
        self._bytes_received += len(bodyBytes)

        # 一点一点的下载
        self.f.write(bodyBytes)

        self.f.flush()

    def connectionLost(self, reason):
        if self._finished.called:
            return
        if reason.check(ResponseDone):
            # 下载完成
            self._finished.callback((self._txresponse, 'success'))
        elif reason.check(PotentialDataLoss):
            # 下载部分
            self._finished.callback((self._txresponse, 'partial'))
        else:
            # 下载异常
            self._finished.errback(reason)

        self.f.close()


class BigfilePipeline(object):
    """
    用于下载大文件
    """
    def process_item(self, item, spider):
        # 创建一个下载文件的任务

        if item['type'] == 'file':
            agent = Agent(reactor)
            d = agent.request(
                method=b'GET',
                uri=bytes(item['url'], encoding='ascii')
            )
            # 当文件开始下载之后，自动执行 self._cb_bodyready 方法
            d.addCallback(self._cb_bodyready, file_name=item['file_name'])

            return d
        else:
            return item

    def _cb_bodyready(self, txresponse, file_name):
        # 创建 Deferred 对象，控制直到下载完成后，再关闭链接
        d = defer.Deferred()
        d.addBoth(self.download_result)  # 下载完成/异常/错误之后执行的回调函数
        txresponse.deliverBody(_ResponseReader(d, txresponse, file_name))
        return d

    def download_result(self, response):
        pass
