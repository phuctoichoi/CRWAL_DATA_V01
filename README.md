# Fruit Crawler Project

Thu thập dữ liệu sản phẩm trái cây bằng Scrapy và hiển thị qua web Flask, kèm tùy chọn tóm tắt nội dung bằng API Ollama.

## Tổng quan
- **Crawler**: `fruit_spider` lấy 5 sản phẩm mẫu từ `hocviennongnghiep.com` (có thể sửa `start_urls` trong `fruit_crawler/spiders/fruit_spider.py`).
- **Định dạng dữ liệu**: JSON Lines (`fruits_data.jsonlines`) gồm `name`, `price`, `image_url`, `original_link`, `description`, `summary`.
- **Web app**: `web_app/app.py` đọc file dữ liệu, hiển thị danh sách và chi tiết sản phẩm, gửi mô tả tới API `http://localhost:11434/api/chat` để tạo summary (mặc định dùng model `llama3`).
- **Chống trùng lặp**: spider và web app tự làm sạch trùng lặp theo `original_link`.

## Cài đặt nhanh
Yêu cầu Python 3.10+.

```bash
cd FruitCrawlerProject
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

## Thu thập dữ liệu với Scrapy
```bash
cd FruitCrawlerProject/scrapy_app
scrapy crawl fruit_spider -O fruits_data.jsonlines
```
- Spider tự phát hiện file dữ liệu nếu đã tồn tại. Có thể chỉ định đường dẫn tuyệt đối qua biến môi trường:
  - Windows: `set FRUITS_DATA_FILE=E:\du-lieu\fruits_data.jsonlines`
  - Linux/macOS: `export FRUITS_DATA_FILE=/path/to/fruits_data.jsonlines`
- Muốn đổi nguồn crawl: chỉnh `start_urls` trong `fruit_crawler/spiders/fruit_spider.py`.

## Chạy web Flask
```bash
cd FruitCrawlerProject/scrapy_app/web_app
python app.py
```
- Mặc định chạy tại `http://localhost:5000`.
- Trang chủ `/` tự làm sạch trùng lặp trước khi hiển thị.
- Trang `/product/<id>` cho phép nhập định dạng tóm tắt; gửi mô tả tới Ollama API và lưu kết quả vào file dữ liệu.

## Thiết lập Ollama (tùy chọn để tóm tắt)
- Cần một server Ollama cục bộ đang chạy API tại `http://localhost:11434`.
- Ví dụ khởi động: `ollama run llama3` (đảm bảo đã tải model trước).
- Nếu không có Ollama, bỏ qua bước tóm tắt; web app vẫn xem dữ liệu đã crawl.

## Cấu trúc thư mục chính
- `scrapy_app/fruit_crawler/spiders/fruit_spider.py`: spider Scrapy.
- `scrapy_app/fruit_crawler/items.py`: định nghĩa trường dữ liệu.
- `scrapy_app/fruit_crawler/settings.py`: cấu hình Scrapy.
- `scrapy_app/web_app/app.py`: ứng dụng Flask + tích hợp Ollama.
- `scrapy_app/web_app/templates/`: giao diện Flask.
- `scrapy_app/web_app/static/`: CSS và logo.
- `scrapy_app/fruits_data.jsonlines`: file dữ liệu mặc định.

## Mẹo & xử lý lỗi
- Kiểm tra robots.txt và tuân thủ khi thay đổi nguồn crawl.
- Nếu lỗi kết nối Ollama: kiểm tra service tại cổng 11434 và tên model.
- Dữ liệu không hiện trên web: xác nhận đường dẫn `FRUITS_DATA_FILE` trỏ đúng file JSON Lines.
- Có thể bật pipeline tóm tắt trong `settings.py` bằng cách bỏ comment `ITEM_PIPELINES` (hiện pipeline chỉ đặt sẵn).

