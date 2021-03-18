import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings

def main():
    # 根据项目配置获取 CrawlerProcess 实例
    process = CrawlerProcess(get_project_settings())

    # 获取 spiderloader 对象，以进一步获取项目下所有爬虫名称
    spider_loader = SpiderLoader(get_project_settings())

    # for spidername in spider_loader.list():
    #     process.crawl(spidername)

    # process.crawl('chinanews')
    process.crawl('tencent')
    # process.crawl('guancha')

    # 执行
    process.start()

if __name__ == '__main__':
    main()