import scrapy

from DarkwebSearch.items import DarkwebsearchItem
from cx_extractor.CxExtractor_python import CxExtractor_python
class DarkwebSpider(scrapy.Spider):
    name = "darkwebSpider"
    start_urls = []  # 清空初始的start_urls
    #allowed_domains = ["ahmia.fi"]
   # proxy_api = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite"
    count_200 = 0
    count_content = 0
    count_nocontent = 0
    content_bad = 0
    def start_requests(self):
        with open('DarkwebSearch/spiders/CyberSecurityKeywords.txt', 'r') as keyword_file:#注意路径
            keywords = keyword_file.read().splitlines()
            #print(keywords)
        for keyword in keywords:
            search_url = f"https://ahmia.fi/search/?q={keyword}"
            proxy_mode = "normal"
            yield scrapy.Request(
                url=search_url,
                callback=self.parse_URL,
                meta={'proxy_mode': proxy_mode,
                      }
            )

    def parse_URL(self, response):
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
            self.count_200 += 1
            print(f"URL:{response.url}status:{response.status} count:{self.count_200}")
            cx = CxExtractor_python()
            content = cx.filter_tags(response.text)
            clean_content = cx.getText(content)
            """if not clean_content:
                print(f"内容{response.url}")"""
            if clean_content:
                self.count_content+=1
                print(f"{self.count_content}提取内容：{response.url}")
                item = DarkwebsearchItem()
                item['URL'] = response.url
                item['Description'] = response.meta.get('site_description')
                item['Content'] = clean_content
                item['Keyword']=response.meta.get('keyword')
                yield item
            else:
                self.count_nocontent+=1
                print(f"{self.count_nocontent}没有内容：{response.url}")
            for href in response.css('a::attr(href)').getall():
                yield response.follow(href, callback=self.parse_site)
        else:
            self.content_bad += 1
            print(f"状态异常：{self.content_bad}")


