# -*- coding: utf-8 -*-
import scrapy
import scrapy_redis
from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from ..items import ScrapyRedisSpidersItem
from scrapy.selector import  HtmlXPathSelector


from bs4 import  BeautifulSoup
from scrapy.http.cookies import CookieJar
import  os

class ChoutiSpider(RedisSpider):

    name = 'chouti'
    allowed_domains = ['chouti.com']
    # start_urls = ['https://dig.chouti.com/']

    # def start_requests(self):
    #     # os.environ['HTTP_PROXY'] = "192.168.10.1"  #代理IP池
    #
    #     for url in self.start_urls:
    #         yield Request(url=url,callback=self.parse_index,meta={'cookiejar':True})
            # yield Request(url=url,callback=self.parse)

    def parse(self,response):
        #response.url获取url
        url = response.url

        yield Request(url=url, callback=self.parse_index, meta={'cookiejar': True})  #meta={'cookiejar': True}表示自动获取cookies

    def parse_index(self,response):
        #登录chouti
        # print(response.text)
        req = Request(
            url='https://dig.chouti.com/login',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                     'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'},
            body='phone=8613163339526&password=466547071&oneMonth=1',
            callback=self.check_login,
            meta={'cookiejar': True}
        )
        # print(req)
        yield req

    def check_login(self,response):
        """
        获取主页信息
        :param response:
        :return:
        """
        print('check_login:',response.text)
        res = Request(
            url='https://dig.chouti.com/',
            method='GET',
            # callback=self.parse_check_login,   #这个去自动点赞功能
            callback=self.parse_images,   #这个是去下载图片功能
            meta={'cookiejar': True},
            dont_filter=True,  #默认是False 默认表示去重   True表示这个url不去重
        )
        print("res:",res)
        yield res


    def parse_check_login(self,response):
        """
        获取主页信息然后进行自动点赞
        :param response:
        :return:
        """
        # print('parse_check_login:',response.text)
        hxs = HtmlXPathSelector(response=response)
        # print(hxs)
        items = response.xpath("//div[@id='content-list']/div[@class='item']")
        # print(items)
        for item in items:
            #点赞带的share-linkid号获取所有的
            linksID = item.xpath(".//div[@class='part2']/@share-linkid").extract_first()
            # print(linksID)
            for nid in linksID:
                res = Request(
                    url='https://dig.chouti.com/link/vote?linksId=%s'%nid,
                    method='POST',
                    callback=self.parse_show_result,
                    meta={'cookiejar': True}  #携带cookies
                )
                yield res

    def parse_show_result(self,response):
        print(response.text)

    def parse_images(self, response):
        """
        下载图片
        :param response:
        :return:
        """
        hxs = HtmlXPathSelector(response=response)
        items = hxs.xpath("//div[@id='content-list']/div[@class='item']")
        for item in items:
            # print(item)
            # href = item.xpath(".//div[@class='part1']//a[1]/@href").extract_first()
            # img = item.xpath("//div[@class='news-pic']/img/@original").extract_first()
            img = item.xpath(".//div[@class='part2']/@share-pic").extract_first()
            # print(img)
            # file_name = img.rsplit('//')[1].rsplit('?')[0]
            img_name = img.rsplit('_')[-1]
            file_path = 'images/{0}'.format(img_name)
            #使用大文件下载方式
            item = ScrapyRedisSpidersItem(url=img, type='file', file_name=file_path)
            print(img)
            yield item

            pages = hxs.xpath("//div[@id='page-area']//a[@class='ct_pagepa']/@href").extract()
            print(pages)
            for page_url in pages:
                #获取所有页码的url
                page_url = "http://dig.chouti.com" + page_url
                print(page_url)
                yield Request(url=page_url, callback=self.parse_images)
