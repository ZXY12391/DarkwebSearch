import scrapy
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time
from DarkwebSearch.items import DarkwebsearchItem
class DarkwebSpider(scrapy.Spider):
    name = "darkwebSpider"
    start_urls = ["https://ahmia.fi/search/?q=drug"]
    #allowed_domains = ["ahmia.fi"]
    proxy_api = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite"

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,meta={'proxy': "http://" + '127.0.0.1:1080'}, dont_filter=True)
    def parse(self, response):
        page = requests.get(self.proxy_api)
        if page.status_code == 200:
            proxy_list = page.text.splitlines()
            for proxy in proxy_list:
                yield scrapy.Request(
                    url=response.url,
                    callback=self.parse_results,
                    meta={'proxy': "http://" + proxy},
                )

    def parse_results(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        results = soup.find(id='ahmiaResultsPage')
        second_results = results.find_all('li', class_='result')

        for result in second_results:
            site_description = result.find('p').text
            site_url = result.find('cite').text
            if not site_url.startswith("http://") and not site_url.startswith("https://"):
                site_url = "http://" + site_url
            item = DarkwebsearchItem()
            item['Description'] =site_description
            item['URL'] = site_url
            yield item
            time.sleep(10)
            yield scrapy.Request(site_url, callback=self.parse_site,meta={'proxy': "http://" + '127.0.0.1:8118'},)

    def parse_site(self, response):
        # 在这个回调函数中处理site_url的内容
        # 你可以从response中提取所需的数据，或者再次发起更多请求
        print(response.url+":"+response.status)
