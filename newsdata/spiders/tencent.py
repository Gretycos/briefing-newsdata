import scrapy
import demjson
from newsdata.items import NewsItem
from datetime import datetime,timedelta

class TencentSpider(scrapy.Spider):
    name = 'tencent'
    allowed_domains = ['i.news.qq.com','inews.gtimg.com','new.qq.com']
    today = datetime.now().date()

    # 请求开始
    def start_requests(self):
        for i in range(0,20,20):
            yield scrapy.Request(url='https://i.news.qq.com/trpc.qqnews_web.kv_srv.kv_srv_http_proxy/list?sub_srv_id=antip&srv_id=pc&offset={}&limit=20&strategy=1&ext={{%22pool%22:[%22high%22,%22top%22],%22is_filter%22:10,%22check_type%22:true}}'.format(i), callback=self.parse)

    def parse(self, response):
        try:
            newsList = demjson.decode(response.body)['data']['list']
        except:
            print("没有找到资源")
            return
        for news in newsList:
            # print(news)
            item = NewsItem()
            item['article_id'] = news['article_id']
            item['media'] = news['media_name']
            item['url'] = news['url']
            item['title'] = news['title']
            item['tags'] = [t['tag_word'] for t in news['tags']]
            item['publish_time'] = news['publish_time']
            publish_date = datetime.strptime(item['publish_time'], '%Y-%m-%d %H:%M:%S').date()
            if publish_date != self.today + timedelta(days=-1):
                continue
            item['images'] = []
            img_url= []
            yield scrapy.Request(url=item['url'], meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302],
            }, callback=self.contentParse, cb_kwargs=dict(item=item,img_url=img_url))

    def contentParse(self,response,item,img_url):
        if response.status == 302:
            yield scrapy.Request(url="https://new.qq.com/rain/a/{}".format(item['article_id']), callback=self.contentParse, cb_kwargs=dict(item=item,img_url=img_url))
        else:
            item['content']='\n'.join([ppath.xpath("normalize-space(string(.))").getall()[0] for ppath in response.xpath("//div[@class='content-article']//p[@class='one-p']")]).strip('\n')

            # 没内容
            if item['content'] == '':
                return

            for i_url in response.xpath("//div[@class='content-article']//img/@src").getall():
                img_url.append('https:{}.jpg'.format(i_url)) # 二进制响应，需要加上.jpg转变成图片格式，否则pipeline无法下载

            # 去除gif图片
            img_url = list(filter(lambda x: 'gif' not in x, img_url))
            item['images_urls'] = img_url

            yield item


