import scrapy
from ..items import FruitCrawlerItem
from datetime import datetime
import json
import os

class MySpider(scrapy.Spider):
    name = 'fruit_spider'

    # Crawl 5 sản phẩm cụ thể
    start_urls = [
        "https://hocviennongnghiep.com/san-pham/cam-c36/",
        "https://hocviennongnghiep.com/san-pham/chuoi-gia-nam/",
        "https://hocviennongnghiep.com/san-pham/vu-sua-bo-hong",
        "https://hocviennongnghiep.com/san-pham/giong-nho-go/",
        "https://hocviennongnghiep.com/san-pham/tao-tay-tao/"
    ]

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.processed_items = set()

        # determine data_file: env FRUITS_DATA_FILE -> scrapy_app/fruits_data.jsonlines -> project_root/fruits_data.jsonlines -> cwd/fruits_data.jsonlines
        env_path = os.getenv('FRUITS_DATA_FILE')
        if env_path:
            self.data_file = env_path
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            candidates = [
                os.path.join(project_dir, 'scrapy_app', 'fruits_data.jsonlines'),
                os.path.join(project_dir, 'fruits_data.jsonlines'),
                os.path.join(os.getcwd(), 'fruits_data.jsonlines'),
            ]
            # pick first existing, otherwise default to scrapy_app location
            self.data_file = next((p for p in candidates if os.path.exists(p)), candidates[0])

        self._load_existing_items()

    def _load_existing_items(self):
        """Tải các original_link đã tồn tại từ file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            item = json.loads(line)
                            if 'original_link' in item:
                                self.processed_items.add(item['original_link'])
                        except json.JSONDecodeError:
                            continue

    def parse(self, response):
        if response.status != 200:
            self.logger.error(f"Truy cập thất bại: {response.url}, mã trạng thái: {response.status}")
            return

        item = FruitCrawlerItem()

        # Lấy tên sản phẩm
        item['name'] = response.css('h1.product_title.entry-title::text').get()
        item['name'] = item['name'].strip() if item['name'] and item['name'].strip() else "Tên không xác định"

        # Lấy giá sản phẩm
        price_text = response.css('p.price span.rt_single_regular_price::text').get()
        if price_text and price_text.strip():
            item['price'] = price_text.replace('đ', '').replace('.', '').strip()
        else:
            price_text = response.css('p.price span.woocommerce-Price-amount.amount bdi::text').get()
            item['price'] = price_text.replace('đ', '').replace('.', '').strip() if price_text and price_text.strip() else "Đang cập nhật"

        # Lấy ảnh và link gốc
        item['image_url'] = response.css('figure.woocommerce-product-gallery__wrapper img.wp-post-image::attr(src)').get()
        item['original_link'] = response.url

        # Gom mô tả
        description_parts = []
        for selector in [
            'div.woocommerce-product-details__short-description ::text',
            'div#tab-description ::text',
            'div.rt_single_short_description ::text'
        ]:
            raw = response.css(selector).getall()
            if raw:
                description_parts.extend([text.strip() for text in raw if text and text.strip()])

        unique_description_parts = list(dict.fromkeys(description_parts))
        item['description'] = '\n'.join(unique_description_parts) if unique_description_parts else "Không có mô tả."

        # Kiểm tra trùng lặp
        item_key = item['original_link']
        if item_key in self.processed_items:
            self.logger.info(f"Bỏ qua sản phẩm trùng lặp: {item_key}")
            return
        self.processed_items.add(item_key)

        yield item