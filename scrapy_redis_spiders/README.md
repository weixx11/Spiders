# scrapy-redis spiders爬虫示例

### 描述

​	根据scrapy-redis常规配置，爬取抽屉网的一个示例，下载抽屉网的图片，以及获取抽屉网新闻url。

### scrapy基本操作

```
scrapy startproject scrapy_redis_spiders  #创建项目
cd scrapy_redis_spiders  #进入目录
scrapy genspider chouti chouti.com   #创建爬虫项目网站
```

### 运行代码

```
scrapy crawl chouti --nolog   #如果查看日志则不要--nolog
```



### 目录结构

- images 下载图片目录
- spiders 爬虫项目网站
  - chouti.py  主要项目操作代码
- items.py 指定保存文件的数据结构
- middlewares.py 中间件，处理request和reponse等相关配置
- pipelines.py  项目管道，可以输出items，改文件里面配置大文件下载
- settings.py 设置文件，常规scrapy-redis配置都在里面
- 起始URL.py  设置传入起始URL到redis中

