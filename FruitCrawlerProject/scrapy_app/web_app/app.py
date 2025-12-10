import json, os, requests, logging
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Khóa bí mật Flask

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Đường dẫn file dữ liệu ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ưu tiên biến môi trường (người dùng có thể set tuyệt đối)
env_path = os.getenv('FRUITS_DATA_FILE')
if env_path:
    DATA_FILE = env_path
else:
    # các vị trí ưu tiên (tương đối trong project)
    possible_paths = [
        os.path.join(BASE_DIR, 'fruits_data.jsonlines'),                 # scrapy_app/fruits_data.jsonlines
        os.path.join(os.path.dirname(BASE_DIR), 'fruits_data.jsonlines') # project_root/fruits_data.jsonlines
    ]
    DATA_FILE = None
    for path in possible_paths:
        if os.path.exists(path):
            DATA_FILE = path
            break
    # nếu không tìm thấy, tạo file mới trong BASE_DIR
    if DATA_FILE is None:
        DATA_FILE = os.path.join(BASE_DIR, 'fruits_data.jsonlines')

# Hàm làm sạch trùng lặp trong file
def clean_duplicates():
    if not os.path.exists(DATA_FILE):
        return []
    seen_links = set()
    unique_fruits = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        item = json.loads(line)
                        if item.get('original_link') and item.get('original_link') not in seen_links:
                            seen_links.add(item.get('original_link'))
                            unique_fruits.append(item)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Lỗi JSON khi làm sạch: {e}")
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            for item in unique_fruits:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        logger.info(f"Làm sạch trùng lặp, còn {len(unique_fruits)} mục")
    except Exception as e:
        logger.error(f"Lỗi khi làm sạch file: {e}")
    return unique_fruits

# Hàm cập nhật summary trong file JSON Lines
def update_jsonlines_file(product_id, new_summary):
    fruits_data = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    fruits_data.append(json.loads(line))
        if 0 <= product_id < len(fruits_data):
            if new_summary.strip():
                fruits_data[product_id]['summary'] = new_summary.strip()
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                for item in fruits_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            logger.info(f"Cập nhật summary cho ID {product_id}")
        else:
            logger.error(f"ID {product_id} không hợp lệ")
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật file: {e}")

# Trang chủ: hiển thị danh sách sản phẩm
@app.route('/')
def index():
    fruits_data = clean_duplicates()  # Làm sạch trùng lặp khi khởi động
    return render_template('index.html', fruits=fruits_data)

@app.route('/about')
def about():
    return render_template('about.html')

# Trang chi tiết sản phẩm + gửi yêu cầu tóm tắt
@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    fruits_data = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    fruits_data.append(json.loads(line))
    except Exception as e:
        logger.error(f"Lỗi khi đọc file: {e}")
        return "Lỗi tải dữ liệu", 500

    if product_id < 0 or product_id >= len(fruits_data):
        return "Không tìm thấy sản phẩm", 404

    fruit = fruits_data[product_id]
    summary = fruit.get('summary', '')

    if request.method == 'POST':
        user_format = request.form.get('format')
        description = fruit.get('description', '')
        if user_format and description:
            try:
                url = "http://localhost:11434/api/chat"
                headers = {"Content-Type": "application/json"}
                prompt = f"{user_format}\n\nMô tả sản phẩm:\n{description}"
                data = {
                    "model": "llama3",
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": "Bạn là AI, tóm tắt nội dung theo định dạng yêu cầu."},
                        {"role": "user", "content": prompt}
                    ]
                }
                response = requests.post(url, headers=headers, json=data, timeout=300)
                response.raise_for_status()
                result = response.json()
                new_summary = result.get("message", {}).get("content", "").strip()
                update_jsonlines_file(product_id, new_summary)
                flash('Tóm tắt đã lưu thành công!', 'success')
                return redirect(url_for('index'))
            except requests.exceptions.RequestException as e:
                logger.error(f"Lỗi API: {e}")
                flash(f'Lỗi API: {str(e)}', 'error')
            except json.JSONDecodeError as e:
                logger.error(f"Lỗi JSON từ API: {e}")
                flash(f'Lỗi JSON từ API: {str(e)}', 'error')
            except Exception as e:
                logger.error(f"Lỗi khác: {e}")
                flash(f'Lỗi khác: {str(e)}', 'error')

    return render_template('product_detail.html', fruit=fruit, summary=summary)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)