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



# class ChoutiSpider(RedisSpider):
#     name = 'chouti'
#     allowed_domains = ['chouti.com']
#     # start_urls = ['http://chouti.com/']
#
#     def parse(self, response):
#         print('url:',response.url)
#         hxs = HtmlXPathSelector(response=response)
#         # 去下载的页面中：找新闻
#         items = hxs.xpath("//div[@id='content-list']/div[@class='item']")
#         # print(items)
#         for item in items:
#             # print(item)
#             href = item.xpath(".//div[@class='part1']//a[1]/@href").extract_first()
#             # img = item.xpath("//div[@class='news-pic']/img/@original").extract_first()
#             # img = item.xpath(".//div[@class='part2']/@share-pic").extract_first()
#             print(href)
#             # file_name = img.rsplit('//')[1].rsplit('?')[0]
#             # img_name = img.rsplit('_')[-1]
#             # file_path='images/{0}'.format(img_name)
#             # item = ImageSpidersItem(url=img,type='file',file_name=file_path)
#             item = ScrapyRedisSpidersItem(url=href)
#             # print(img)
#             yield item





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


# # class ChoutiSpider(scrapy.Spider):
# #     name = 'chouti'
# #     allowed_domains = ['chouti.com']
# #     start_urls = ['https://dig.chouti.com/']
# #     cookies = None
# #
# #
# #     def parse(self, response):
# #         # 此时只是拿到了一个存储cookie的容器
# #         cookie_obj = CookieJar()
# #
# #         # response表示请求的所有内容，response.request表示我们发的请求
# #         # 接受我们上面说的两个参数
# #         cookie_obj.extract_cookies(response, response.request)
# #
# #         # 那么此时的cookie_obj便保存了我们的cookie信息
# #         print(cookie_obj._cookies)
# #
# #         '''
# #                 {'.chouti.com': {'/': {'gpsd': Cookie(version=0, name='gpsd', value='1c61978d6bb94989674386b29f2fd15d', port=None, port_specified=False, domain='.chouti
# #         .com', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=1533183431, discard=False, comment=None, co
# #         mment_url=None, rest={}, rfc2109=False)}}, 'dig.chouti.com': {'/': {'JSESSIONID': Cookie(version=0, name='JSESSIONID', value='aaaouDhGaca3Ugddzblrw', po
# #         rt=None, port_specified=False, domain='dig.chouti.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, e
# #         xpires=None, discard=True, comment=None, comment_url=None, rest={}, rfc2109=False)}}}
# #                 '''
# #         # 上面便是我们获取的cookie信息
# #
# #         # 将cookie保存起来
# #         self.cookies = cookie_obj._cookies
# #
# #         # 同理request也一样
# #         '''
# #         类似于requests
# #         res = requests.get(xxxxx)
# #         res.cookies._cookies便是返回的cookie信息
# #         '''
# #
# #         # 然后就要模拟登陆了，带上用户名和密码和cookie
# #         yield Request(
# #             url='https://dig.chouti.com/login',
# #             method='POST',
# #             headers={'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
# #                      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'},
# #             cookies=self.cookies,
# #             callback=self.check_login,
# #             # 这里的body类似于requests的data，但是形式不一样，body不能够以字典的形式提交
# #             # 账号密码输入的对的，这里隐藏了
# #             body='phone=8613163339526&password=466547071&oneMonth=1'
# #         )
# #
# #
# #     # 回调函数，用于检测请求是否发送成功。
# #     # 注意回调函数不能是self.parse，否则回调执行的时候又把请求发过去了
# #     # 里面自动封装了response，就是我们执行成功之后的响应结果
# #     def check_login(self, response):
# #         print(response.text)
# #         '''
# #         {"result":{"code":"9999", "message":"", "data":{"complateReg":"0","destJid":"cdu_53059370687"}}}
# #         '''
# #         # 登陆成功
# #
# #         # 接下来进行点赞。
# #         # 登陆页面不需要cookie
# #         # 依旧yield
# #         yield Request(
# #             url='https://dig.chouti.com/',
# #             callback=self.like,  # 定义一个用于点赞的回调函数
# #         )
# #
# #
# #     def like(self, response):
# #         # 此时的response则是整个页面
# #         id_list = response.xpath('//div[@share-linkid]/@share-linkid').extract()
# #         for nid in id_list:
# #             url = 'https://dig.chouti.com/link/vote?linksId=%s' % nid
# #             yield Request(
# #                 url=url,
# #                 method='POST',
# #                 cookies=self.cookies,
# #                 headers={'referer': 'https://dig.chouti.com/'},
# #                 # 再加一个回调函数，查看是否点赞成功
# #                 callback=self.show_like
# #             )
# #
# #
# #     def show_like(self, response):
# #         print(response.text)