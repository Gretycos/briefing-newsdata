# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    article_id = scrapy.Field()
    media = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    publish_time = scrapy.Field()
    images = scrapy.Field() # 存放下载下来的磁盘路径
    images_urls = scrapy.Field() # 存放要访问的远程路径


