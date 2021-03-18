import scrapy
import demjson
from newsdata.items import NewsItem
import time
from datetime import datetime,timedelta

class ChinanewsSpider(scrapy.Spider):
    name = 'chinanews'
    allowed_domains = ['channel.chinanews.com','www.chinanews.com','i2.chinanews.com']
    today = datetime.now().date()

    # 请求开始
    def start_requests(self):
        for i in range(0, 2):
            yield scrapy.Request(url='http://channel.chinanews.com/cns/s/5013.shtml?pager={}&pagenum=100&_={}'.format(i,int(round(time.time()*1000))), callback=self.parse)

    def parse(self, response):
        newsList = demjson.decode(response.text[17:-29])['docs']
        for news in newsList:
            item = NewsItem()
            item['article_id'] = news['id']
            item['url'] = news['url']
            if 'shipin' in item['url']:
                continue
            item['title'] = news['title']
            item['publish_time'] = news['pubtime']
            publish_date = datetime.strptime(item['publish_time'], '%Y-%m-%d %H:%M:%S').date()
            if publish_date != self.today + timedelta(days=-1):
                continue
            item['images'] = []
            img_url = []
            yield scrapy.Request(url=item['url'], callback=self.contentParse, cb_kwargs=dict(item=item, img_url=img_url))

    def contentParse(self,response,item,img_url):
        item['tags'] = response.xpath("//meta[contains(@name,'keywords')]/@content").get().split(",")
        left_t = response.xpath("string(//div[@class='left-t'])").get()
        item['media'] = left_t[left_t.find('：')+1:-4]
        item['content'] = '\n'.join([ppath.xpath("normalize-space(string(.))").getall()[0] for ppath in response.xpath("//div[@class='left_zw']//p")]).strip('\n')

        # 没内容
        if item['content'] == '':
            return

        img_url.extend(response.xpath("//div[@class='left_ph']//img/@src").getall())
        img_url.extend(response.xpath("//div[@class='left_zw']//img/@src").getall())

        # 去除gif图片
        img_url = filter(lambda x:'gif' not in x,img_url)
        item['images_urls'] = img_url

        yield item