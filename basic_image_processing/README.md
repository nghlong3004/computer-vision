# Basic Image Processing 

Bài tập môn Thị Giác Máy.
Dự án xây dựng một quy trình xử lý ảnh cơ bản sử dụng **Python**, **OpenCV**.

## Yêu cầu bài toán (Project Requirements)

Chương trình thực hiện các tác vụ xử lý ảnh sau:
1. [x] Chọn và đọc ảnh màu bất kỳ.
2. [x] Hiển thị thông tin kích thước ảnh (Metadata).
3. [x] Hiển thị ảnh gốc.
4. [x] Tách và hiển thị các kênh màu riêng biệt (R, G, B).
5. [x] Chuyển đổi thứ tự kênh màu (Channel Swapping: BGR -> RGB) và lưu ảnh.
6. [x] Chuyển đổi sang ảnh xám.
7. [x] Chuyển đổi sang ảnh nhị phân.

## Cài đặt & Môi trường (Installation)

Dự án yêu cầu **Python 3.8+**.

### 1. Clone hoặc tải project về máy
git clone https://github.com/nghlong3004/computer-vision
Đảm bảo cấu trúc thư mục như sau:

```bash
basic_image_processing/
├── assets/                 # Thư mục chứa tài nguyên
│   ├── sample.jpg          # Ảnh đầu vào (Input)
│   └── output_swapped.jpg  # Ảnh kết quả sau khi xử lý (Output)
├── src/                    # Thư mục mã nguồn chính 
│   ├── __init__.py         # Đánh dấu thư mục là một Python Package
│   └── image_processor.py  # Module chứa Class xử lý ảnh
├── main.py                 # File chạy chương trình
├── requirements.txt        # Danh sách các thư viện phụ thuộc
└── README.md               # Tài liệu hướng dẫn sử dụng
```

### 2. Cài đặt thư viện

```bash
cd basic_image_processing
pip install -r requirements.txt
```

### 3. Hướng dẫn sử dụng

1. Đặt một file ảnh bất kỳ vào thư mục assets/ và đổi tên thành sample.jpg (hoặc sửa đường dẫn trong main.py).

2. Chạy chương trình
```bash
python main.py
```

3. Tương tác

Các cửa sổ ảnh sẽ hiện lên lần lượt.

Nhấn bất kỳ phím nào vào cửa sổ ảnh để đóng chương trình.

Ảnh sau khi xử lý sẽ được lưu tự động vào thư mục assets/ với tên output_swapped.jpg.


