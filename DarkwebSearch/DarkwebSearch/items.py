# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DarkwebsearchItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Description=scrapy.Field()
    URL=scrapy.Field()
    Content=scrapy.Field()
    Keyword=scrapy.Field()
    #仅做标记，实际不需要
    Type=scrapy.Field()#记录能不能从html直接抽取信息，如果不能就把获取到的html的标签清洗掉

