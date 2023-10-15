import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class GoogleSpider(scrapy.Spider):
    name = "google"
    allowed_domains = ["www.yahoo.com"]
    start_urls = ["https://www.yahoo.com/news/cloud-gaming-firm-shadow-says-150514052.html"]

    def parse(self, response):
        proxy_ip = response.request.meta.get('proxy')
        print(f"Using proxy IP: {proxy_ip}")
        # print(response.status)
       # print(response.text)
