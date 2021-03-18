# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interfac
from scrapy import Request
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

from newsdata.model import loadSession
from newsdata.model.News import News
from newsdata.settings import IMAGES_STORE


class ImgsPipeline(ImagesPipeline):
    # 在settings中的主目录下，每张图片的具体位置与名字
    def file_path(self, request, response=None, info=None, *, item=None):
        adapter = ItemAdapter(item)
        page_name = request.url.split("/")[-1]
        return '/{}/{}/{}'.format(adapter['publish_time'].split(' ')[0],adapter['article_id'],'{}.jpg'.format(request.url.split("/")[-2]) if '1000' in page_name else page_name)

    # 下载图片
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for image_url in adapter['images_urls']:
            yield Request(url=image_url)

    # 下载完成
    def item_completed(self, results, item, info):
        image_paths = ['{}{}'.format(IMAGES_STORE,image['path']) for ok, image in results if ok]
        # if not image_paths:
        #     raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter['images'] = image_paths
        return item

class NewsdataPipeline(object):
    # 构造函数
    def __init__(self):
        self.session = loadSession()
        self.count=0

    # 处理传递过来的item
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        newNews = News(
            article_id=adapter['article_id'],
            media=adapter['media'],
            url=adapter['url'],
            title=adapter['title'],
            tags=adapter['tags'],
            content=adapter['content'],
            publish_time=adapter['publish_time'],
            images=adapter['images'],
        )
        try:
            # 分batch commit 否则会出现因连接丢失导致数据包无法读取的问题
            self.count += 1
            if self.count % 10 == 0:
                print("========提交到数据库========")
                self.session.commit()
            # 如果pk不存在则从db中query出来合并，如果db中没有则insert新instance
            # query前会flush，如果insert语句堆积会导致连接丢失，必须要分batch commit
            self.session.merge(newNews)
            return item
        except Exception as e:
            self.session.rollback()
            print("========提交/合并失败，出现异常，回滚。========\n原因:{}".format(e))

    # 关闭爬虫
    def close_spider(self,spider):
        try:
            print("========提交到数据库========")
            self.session.commit()
        except Exception as e:
            print("========提交失败，出现异常，回滚。========\n原因:{}".format(e))
            self.session.rollback()
        finally:
            print("========结束会话========")
            self.session.close()
