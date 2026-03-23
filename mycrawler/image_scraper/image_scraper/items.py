import scrapy

class ImageScraperItem(scrapy.Item):
    category = scrapy.Field()
    keyword = scrapy.Field()   # 新增：记录具体是哪个场景/关键词
    image_urls = scrapy.Field()
    images = scrapy.Field()