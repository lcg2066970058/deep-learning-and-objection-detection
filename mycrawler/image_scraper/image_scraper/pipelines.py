import os
import threading
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request


class CategoryImagesPipeline(ImagesPipeline):
    TARGET_TOTAL = 100  # 每个类别的总目标
    _category_locks = {}
    _keyword_counters = {}  # 记录每个场景(keyword)已下载的数量

    def _get_category_lock(self, category):
        if category not in self._category_locks:
            self._category_locks[category] = threading.Lock()
        return self._category_locks[category]

    def _get_valid_image_count(self, category):
        """统计该类别总共下载了多少张"""
        category_dir = os.path.join(self.store.basedir, category)
        if not os.path.exists(category_dir):
            return 0
        valid_files = [
            f for f in os.listdir(category_dir)
            if f.endswith('.jpg') and f.startswith(f'{category}_')
        ]
        return len(valid_files)

    def _get_quota(self, category, keyword):
        """【核心】计算当前场景的配额：如果超过平均配额，就丢弃"""
        lock = self._get_category_lock(category)

        with lock:
            # 初始化该类别的场景计数器
            if category not in self._keyword_counters:
                self._keyword_counters[category] = {}
            if keyword not in self._keyword_counters[category]:
                self._keyword_counters[category][keyword] = 0

            # 计算该类别下总共有多少个不同的场景（从spider传入的meta或全局获取，这里简化处理，直接预估一个合理值）
            # 为了简单，我们设定每个场景最多占 1/6 的配额，防止某一个场景霸榜
            max_per_keyword = self.TARGET_TOTAL // 5

            # 如果这个场景已经下载够了，返回 False
            if self._keyword_counters[category][keyword] >= max_per_keyword:
                return False

            return True

    def get_media_requests(self, item, info):
        category = item['category']
        keyword = item['keyword']
        current_total = self._get_valid_image_count(category)

        # 总数已满，直接丢弃
        if current_total >= self.TARGET_TOTAL:
            raise DropItem(f"【{category}】已完成{self.TARGET_TOTAL}张，停止下载")

        # 检查该场景是否还有配额
        if not self._get_quota(category, keyword):
            raise DropItem(f"【{category}-{keyword}】场景配额已用完，跳过")

        for image_url in item['image_urls']:
            yield Request(
                image_url,
                meta={'category': category, 'keyword': keyword},
                dont_filter=True
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        category = request.meta['category']
        keyword = request.meta['keyword']
        lock = self._get_category_lock(category)

        with lock:
            current_count = self._get_valid_image_count(category)
            if current_count >= self.TARGET_TOTAL:
                raise DropItem(f"【{category}】已达到{self.TARGET_TOTAL}张")

            # 生成文件名
            next_index = current_count + 1
            filename = f"{category}_{next_index:03d}.jpg"

            # 增加该场景的计数
            if category in self._keyword_counters and keyword in self._keyword_counters[category]:
                self._keyword_counters[category][keyword] += 1

            return os.path.join(category, filename)

    def item_completed(self, results, item, info):
        category = item['category']
        keyword = item['keyword']
        success_images = [x for ok, x in results if ok]

        if not success_images:
            # 如果失败了，把刚才加的计数减回去
            lock = self._get_category_lock(category)
            with lock:
                if category in self._keyword_counters and keyword in self._keyword_counters[category]:
                    self._keyword_counters[category][keyword] -= len(success_images)
            raise DropItem(f"【{category}-{keyword}】该批次图片全部下载失败")

        current_total = self._get_valid_image_count(category)
        self.logger.info(f"【{category}】累计: {current_total}/{self.TARGET_TOTAL} (当前场景: {keyword})")

        item['downloaded_images'] = success_images
        return item