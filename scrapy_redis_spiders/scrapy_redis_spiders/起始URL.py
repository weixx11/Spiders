#!/usr/bin/env python
#coding=utf-8

import redis

conn = redis.Redis(host='127.0.0.1',port=6379)

# 起始url的Key： chouti:start_urls
conn.lpush("chouti:start_urls",'https://dig.chouti.com')
v = conn.keys()
# value = v.mget("chouti:start_urls")
# v1 = conn.lpop('chouti:start_urls')
print(v)
# print(v1)

# conn.flushall()