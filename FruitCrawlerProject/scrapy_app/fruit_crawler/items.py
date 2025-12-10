import scrapy  # Thư viện Scrapy để định nghĩa Item

class FruitCrawlerItem(scrapy.Item):
    # Khai báo các trường dữ liệu cần thu thập
    name = scrapy.Field()          # Tên sản phẩm
    price = scrapy.Field()         # Giá sản phẩm
    image_url = scrapy.Field()     # Link ảnh sản phẩm
    original_link = scrapy.Field() # Link gốc của sản phẩm
    description = scrapy.Field()   # Mô tả chi tiết
    summary = scrapy.Field()       # Tóm tắt sản phẩm
