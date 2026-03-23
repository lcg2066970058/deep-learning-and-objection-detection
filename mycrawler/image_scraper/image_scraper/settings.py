BOT_NAME = 'image_scraper'
SPIDER_MODULES = ['image_scraper.spiders']
NEWSPIDER_MODULE = 'image_scraper.spiders'

ROBOTSTXT_OBEY = False
IMAGES_STORE = 'imgs'

ITEM_PIPELINES = {
    'image_scraper.pipelines.CategoryImagesPipeline': 1,
}

IMAGES_MIN_WIDTH = 200
IMAGES_MIN_HEIGHT = 200

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://image.baidu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 2
COOKIES_ENABLED = True
MEDIA_ALLOW_REDIRECTS = True
RETRY_TIMES = 5