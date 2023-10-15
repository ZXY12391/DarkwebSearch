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
class DarkwebSpider(scrapy.Spider):
    name = "darkwebSpider"
    start_urls = []  # 清空初始的start_urls
    #allowed_domains = ["ahmia.fi"]
    proxy_api = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite"

    def start_requests(self):
        with open('DarkwebSearch/spiders/CyberSecurityKeywords.txt', 'r') as keyword_file:#注意路径
            keywords = keyword_file.read().splitlines()
        for keyword in keywords:
            search_url = f"https://ahmia.fi/search/?q={keyword}"
            proxy_mode = "normal"
            yield scrapy.Request(
                url=search_url,
                callback=self.parse_URL,
                meta={'proxy_mode': proxy_mode}
            )

    def parse_URL(self, response):
        lis = response.xpath("//*[@id='ahmiaResultsPage']/ol/li")
        for li in lis:
            site_description = li.xpath("./h4/a/text()").extract_first().strip()
            site_url = li.xpath("./cite/text()").extract_first()
            if not site_url.startswith("http://") and not site_url.startswith("https://"):
                site_url = "http://" + site_url
            item = DarkwebsearchItem()
            item['Description'] = site_description
            item['URL'] = site_url
            yield item
            proxy_mode = "strict"
            yield scrapy.Request(
                url=site_url,
                callback=self.parse_site,
                meta={'proxy_mode': proxy_mode}
            )

    def parse_site(self, response):
        print(f"URL: {response.url}, Status: {response.status}")
        cleaned_url = re.sub(r'[\/:*?"<>|]', ' ', response.url)
        unique_filename = f"{cleaned_url}.html"
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_directory, unique_filename)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
