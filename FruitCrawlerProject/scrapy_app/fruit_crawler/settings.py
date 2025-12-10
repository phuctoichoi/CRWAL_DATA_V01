# Cài đặt Scrapy project
BOT_NAME = 'fruit_crawler'

SPIDER_MODULES = ['fruit_crawler.spiders']
NEWSPIDER_MODULE = 'fruit_crawler.spiders'

# User-Agent để giả lập trình duyệt, tránh bị chặn
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Tuân thủ robots.txt (Quan trọng!)
ROBOTSTXT_OBEY = True

# Cấu hình tải xuống chậm hơn để tránh bị chặn IP
DOWNLOAD_DELAY = 1  # 1 giây giữa mỗi request
# CONCURRENT_REQUESTS = 1 # Nếu cần cực kỳ chậm, chỉ xử lý 1 request cùng lúc

# Bỏ comment dòng này để bật pipeline của chúng ta
#ITEM_PIPELINES = {
  # 'fruit_crawler.pipelines.OllamaSummarizationPipeline': 300,
#}

# Cấu hình để output ra file JSON mà không bị ghi đè
FEED_EXPORT_ENCODING = 'utf-8' # Đảm bảo encoding cho tiếng Việt

# Logging level (tuỳ chọn)
# LOG_LEVEL = 'INFO'