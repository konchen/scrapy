# -*- coding: utf-8 -*-
from scrapy import Spider,Request
from ..items import UserItem
import json
class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'  #用户，他关注列表，关注他的列表的url通用表达式
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    #获取第一个用户的url,他关注的用户列表第一页，关注他的用户列表第一页

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query),self.parse_user)
        yield Request(self.follows_url.format(user=self.start_user,include=self.follows_query,offset=0,limit=20),self.parse_follows)
        yield Request(self.followers_url.format(user=self.start_user,include=self.followers_query,offset=0,limit=20),self.parse_followers)

    def parse_user(self,response): #通用：解析用户url，提取参数；设置所有用户关注的用户列表第一页，关注他的用户列表第一页，实现层层递归
        item = UserItem()
        result = json.loads(response.text)
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield Request(self.follows_url.format(user=result.get('url_token'),include=self.follows_query,offset=0,limit=20),self.parse_follows)
        yield Request(self.followers_url.format(user=result.get('url_token'),include=self.followers_query,offset=0,limit=20),self.parse_followers)

    def parse_follows(self,response):  #解析所有用户关注的用户列表网页，得到用户
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),self.parse_user) #回调用户解析函数，并得到该用户的关注列表
        if 'paging' in results.keys() and results.get('paging').get('is_end')==False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,self.parse_follows) #递归翻页

    def parse_followers(self,response): #解析所有关注他的用户列表网页，得到用户
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),self.parse_user) #回调用户解析函数
        if 'paging' in results.keys() and results.get('paging').get('is_end')==False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,self.parse_followers) #递归翻页




