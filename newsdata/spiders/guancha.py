import scrapy
import demjson
from newsdata.items import NewsItem
from datetime import datetime,timedelta

class GuanchaSpider(scrapy.Spider):
    name = 'guancha'
    allowed_domains = ['www.guancha.cn']
    today = datetime.now().date()

    # 请求开始
    def start_requests(self):
        for i in range(1, 3):
            yield scrapy.Request(url='https://www.guancha.cn/xinguan/list_{}.shtml'.format(i), callback=self.parse)

    def parse(self, response):
        newsList =  response.xpath("//ul[contains(@class,'column-list')]//li")
        for news in newsList:
            item = NewsItem()
            item['article_id'] = news.xpath("./h4[@class='module-title']/a/@href").get().split('/')[-1].split('.')[0]
            item['url'] = 'https://www.guancha.cn{}'.format(news.xpath("./h4[@class='module-title']/a/@href").get())
            item['title'] = news.xpath("string(./h4[@class='module-title']/a)").get()
            item['publish_time'] = news.xpath("string(./div[@class='module-interact']/span)").get()
            publish_date = datetime.strptime(item['publish_time'],'%Y-%m-%d %H:%M:%S').date()
            if publish_date != self.today + timedelta(days=-1):
                continue
            item['images'] = []
            img_url = []
            yield scrapy.Request(url=item['url'], callback=self.contentParse, cb_kwargs=dict(item=item, img_url=img_url))

    def contentParse(self,response,item,img_url):
        item['tags'] = [tpath.xpath("string(.)").get() for tpath in response.xpath("//div[@class='key-word fix mt15']//a") if len(tpath.xpath("string(.)").get())!=0]
        item['media'] = response.xpath("string(//div[@class='time fix']/span[3])").get().split("：")[-1]
        item['content'] = '\n'.join([ppath.xpath("normalize-space(string(.))").getall()[0] for ppath in response.xpath("//div[@class='content all-txt']//p[not(@style or @align)]")]).strip('\n')

        # 没内容
        if item['content'] == '':
            return

        img_url.extend(response.xpath("//div[@class='content all-txt']//img/@src").getall())

        # 去除gif图片
        img_url = filter(lambda x:'gif' not in x,img_url)
        item['images_urls'] = img_url

        yield item
