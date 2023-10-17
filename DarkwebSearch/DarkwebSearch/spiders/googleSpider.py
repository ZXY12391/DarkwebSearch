import scrapy
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time
import os
from DarkwebSearch.items import DarkwebsearchItem
from random import choice
import re
from cx_extractor.CxExtractor_python import CxExtractor_python
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.connection import get_redis_from_settings
from DarkwebSearch.settings import REDIS_HOST,REDIS_PORT,REDIS_DB,REDIS_PARAMS
from scrapy_redis.spiders import RedisSpider  # 导入 RedisSpider

from scrapy_redis.connection import get_redis
import redis
class GoogleSpider(RedisSpider):
    name = "googleSpider"
    redis_key = "search_url"
    count_200=0
    count_content=0
    count_nocontent=0
    content_bad=0

    def __init__(self, *args, **kwargs):
        super(GoogleSpider, self).__init__(*args, **kwargs)

        # 请替换为您自己的Redis连接信息
        redis_host = REDIS_HOST
        redis_port = REDIS_PORT
        redis_db = REDIS_DB
        redis_password=REDIS_PARAMS.get('password')

        # 在这里实现您的URL生成逻辑
        urls_to_push = []
        with open('DarkwebSearch/spiders/CyberSecurityKeywords.txt', 'r') as keyword_file:
            keywords = keyword_file.read().splitlines()
        for keyword in keywords:
            url = f'https://ahmia.fi/search/?q={keyword}'
            urls_to_push.append(url)
        # 将URL推送到Redis队列
        self.push_urls_to_redis(redis_host,redis_password,redis_port, redis_db, urls_to_push)


    def push_urls_to_redis(self, host,password,port, db, urls):
        redis_conn = redis.StrictRedis(host=host,password=password, port=port, db=db)
        for url in urls:
            redis_conn.lpush('search_url', url)
    def parse(self, response):
        lis = response.xpath("//*[@id='ahmiaResultsPage']/ol/li")
        for li in lis:
            site_description = li.xpath("./h4/a/text()").extract_first().strip()
            site_url = li.xpath("./cite/text()").extract_first()
            if not site_url.startswith("http://") and not site_url.startswith("https://"):
                site_url = "http://" + site_url
            proxy_mode = "Tor"
            # 获取关键字并存储到Item中
            keyword = response.url.split("=")[-1]
            yield scrapy.Request(
                url=site_url,
                callback=self.parse_site,
                meta={'proxy_mode': proxy_mode,
                      'site_description':site_description,
                      'keyword':keyword
                      }
            )

    def parse_site(self, response):
        #print(f"URL: {response.url}, Status: {response.status}")
        """cleaned_url = re.sub(r'[\/:*?"<>|]', ' ', response.url)
        unique_filename = f"{cleaned_url}.html"
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_directory, unique_filename)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)"""
        if response.status==200:
            self.count_200+=1
            print(f"URL:{response.url}status:{response.status} count:{self.count_200}")
            cx = CxExtractor_python(threshold=186)
            filter_content = cx.filter_tags(response.text)
            clean_content = cx.getText(filter_content)
            """if not clean_content:
                print(f"没有内容{response.url}")"""
            item = DarkwebsearchItem()
            item['URL'] = response.url
            item['Description'] = response.meta.get('site_description')
            item['Keyword'] = response.meta.get('keyword')
            if clean_content:
                item['Content'] = clean_content
                item['Type'] = "extract"#仅做标记，实际不需要
                self.count_content += 1
                print(f"{self.count_content}提取内容:{response.url}")
                yield item
            else:
                content=cx.filter_tags1(response.text)
                item['Content'] = content
                item['Type'] = "filter"
                self.count_nocontent+=1
                print(f"{self.count_nocontent}没有提取到内容：{response.url}")
        else:
            self.content_bad+=1
            print(f"状态异常：{self.content_bad}")



