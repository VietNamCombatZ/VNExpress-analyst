# README – Hướng dẫn chạy chương trình

## 1. Giới thiệu

Dự án này thu thập và phân tích dữ liệu bài viết tin tức từ trang báo điện tử VnExpress.
Quy trình thực hiện gồm các bước:

1. Crawl dữ liệu bài viết.
2. Làm sạch và tiền xử lý dữ liệu.
3. Phân tích và trực quan hóa dữ liệu.

---

# 2. Cấu trúc thư mục

```
VNExpress-analyst/
│
├── data/
│   ├── raw_data/        # dữ liệu thô sau khi crawl
│   └── clean_data.csv      # dữ liệu sau khi làm sạch
│
├── notebooks/           # các notebook phân tích dữ liệu
│   ├── 00_*.ipynb
│   ├── 01_*.ipynb
│   ├── 02_*.ipynb
│   ├── 03_*.ipynb
│   ├── 04_*.ipynb
│   └── 05_*.ipynb
│
├── scripts/
│   └── crawl_data.py    # script crawl dữ liệu
│
└── requirement.txt      # danh sách thư viện cần cài
```

---

# 3. Cài đặt môi trường

Khuyến nghị sử dụng **Python virtual environment**.

### Tạo môi trường ảo

```bash
python -m venv .venv
```

### Kích hoạt môi trường

MacOS / Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### Cài đặt các thư viện cần thiết

Tất cả thư viện Python đã được liệt kê trong file `requirement.txt`.

```bash
pip install -r requirement.txt
```

---

# 4. Trình tự chạy chương trình

## Bước 1: Crawl dữ liệu

Di chuyển vào thư mục `scripts` và chạy file crawl:

```bash
cd scripts
python crawl_data.py
```

Sau khi chạy xong, dữ liệu thô sẽ được lưu vào thư mục:

```
data/raw_data/
```

---

## Bước 2: Chạy các notebook phân tích dữ liệu

Sau khi crawl xong dữ liệu, di chuyển vào thư mục `notebooks`:

```bash
cd ../notebooks
```

Mở **Jupyter Notebook** hoặc **JupyterLab** và chạy các notebook **theo đúng thứ tự**:

```
00 → 01 → 02 → 03 → 04 → 05
```

Ví dụ:

```
00_data_overview.ipynb
01_raw_data_overview.ipynb
02_clean_data_overview.ipynb
03_data_encoding.ipynb
04_feature_engineering.ipynb
05_news_classification.ipynb
```

Các notebook này lần lượt thực hiện:

1. Khảo sát dữ liệu thô
2. Làm sạch dữ liệu
3. Tiền xử lý văn bản
4. Phân tích dữ liệu
5. Trực quan hóa
6. Xây dựng đặc trưng

---

# 5. Lưu ý

* Cần **chạy file crawl_data.py trước** khi chạy các notebook.
* Các notebook phải được chạy **theo đúng thứ tự** để đảm bảo dữ liệu đầu vào của bước sau được tạo từ bước trước.
* Dữ liệu sau khi làm sạch sẽ được lưu trong file:

```
data/clean_data.csv
```

---

# 6. Yêu cầu hệ thống

* Python ≥ 3.10
* Internet (để crawl dữ liệu)
* Google Chrome (dùng cho Selenium khi crawl dữ liệu)

---
