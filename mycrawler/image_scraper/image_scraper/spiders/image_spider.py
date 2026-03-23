import scrapy
import json
import os
import random
from ..items import ImageScraperItem


class ImageSpider(scrapy.Spider):
    name = 'image_spider'
    allowed_domains = ['image.baidu.com']

    CATEGORIES = {
        # 苹果：桌子上、人手上、人正在吃、超市、树上、切开、水果拼盘
        'apple': [
            '苹果', '苹果 放在桌子上', '苹果 拿在手上', '人正在吃苹果',
            '苹果 在超市货架', '苹果 在树上', '切开的苹果', '水果拼盘 苹果'
        ],

        # 西瓜：完整、切开、冰箱里、人拿着、水果摊、田里
        'watermelon': [
            '西瓜', '完整的西瓜', '切开的西瓜', '西瓜 放在冰箱里',
            '人 拿着西瓜', '西瓜 在水果摊', '西瓜 在田里 地里'
        ],

        # 飞机：停在机场、空中飞行、电视里、玩具模型、军事飞机、客机
        'airplane': [
            '飞机', '飞机 停在机场', '飞机 空中飞行', '飞机 电视画面',
            '玩具飞机 模型', '军事飞机 战斗机', '客机 民航飞机'
        ],

        # 摩托车：行驶中、停靠、赛车、不同角度、有人骑、无人
        'motorcycle': [
            '摩托车', '摩托车 行驶中 道路', '摩托车 停靠在路边', '摩托车 赛车',
            '摩托车 正面 侧面 背面', '人 骑着摩托车', '摩托车 无人 静态'
        ],

        # 雨伞
        'umbrella': [
            '雨伞', '雨伞 雨中', '雨伞 遮阳', '雨伞 撑开', '雨伞 收起'
        ],

        # 水杯
        'cup': [
            '水杯', '水杯 放在桌子上', '水杯 喝水', '水杯 厨房', '水杯 办公室'
        ],

        # 人类：全身、半身、不同动作、多人、不同年龄段
        'human': [
            '人物 全身照', '人物 半身照', '人 走路', '人 坐着', '人 跑步',
            '多人 合影', '小孩 儿童', '年轻人', '中年人', '老年人 老人'
        ],

        # 小汽车
        'car': [
            '小汽车', '汽车 道路行驶', '汽车 停车场', '汽车 赛车', 'SUV 轿车'
        ],

        # 猫：沙发上、户外、玩玩具、睡觉、被抱着
        'cat': [
            '猫', '猫 在沙发上', '猫 户外 草地', '猫 玩玩具', '猫 睡觉', '猫 被人抱着'
        ],

        # 狗：散步、奔跑、与人互动、公园、各种品种
        'dog': [
            '狗', '狗 散步', '狗 奔跑', '狗 与人互动', '狗 在公园',
            '金毛犬', '哈士奇', '柯基犬', '泰迪犬', '拉布拉多'
        ]
    }

    BASE_URL = 'https://image.baidu.com/search/acjson?tn=resultjson_com&word={word}&pn={pn}&rn=30'

    def start_requests(self):
        target_count = 100
        all_requests = []

        for category, keywords in self.CATEGORIES.items():
            # 检查是否已经完成
            category_dir = os.path.join('imgs', category)
            if os.path.exists(category_dir):
                current_count = len([
                    f for f in os.listdir(category_dir)
                    if f.endswith('.jpg') and f.startswith(f'{category}_')
                ])
                if current_count >= target_count:
                    self.logger.info(f"【{category}】已完成{target_count}张，跳过爬取")
                    continue

            # 生成请求，但先不立即 yield，而是放入列表准备打乱
            for keyword in keywords:
                # 每个场景只爬 3 页，避免一次性下太多，给其他场景留机会
                for page in range(3):
                    url = self.BASE_URL.format(word=keyword, pn=page * 30)
                    all_requests.append(
                        scrapy.Request(
                            url,
                            callback=self.parse,
                            meta={'category': category, 'keyword': keyword},
                            dont_filter=True
                        )
                    )

        # 【关键】打乱所有请求的顺序，防止按顺序下载导致场景不均
        random.shuffle(all_requests)

        # 发出打乱后的请求
        for req in all_requests:
            yield req

    def parse(self, response):
        category = response.meta['category']
        keyword = response.meta['keyword']

        try:
            data = json.loads(response.text)
            if 'data' not in data:
                return
            urls = []
            for img in data['data']:
                if 'middleURL' in img:
                    urls.append(img['middleURL'])
            if urls:
                item = ImageScraperItem()
                item['category'] = category
                item['keyword'] = keyword  # 把场景名传给 pipeline
                item['image_urls'] = urls
                yield item
        except Exception as e:
            self.logger.error(f"解析出错: {e}")