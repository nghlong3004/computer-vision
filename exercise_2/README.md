# Spatial Smoothing Filtering

Project này giải bài toán lọc theo yêu cầu đề bài, tập trung vào clean code, OOP, SOLID và phân tách clean architecture.

## Đề bài

Chương trình thực hiện đầy đủ các yêu cầu sau:

1. Chọn ngẫu nhiên một bức ảnh trong thư mục `assets/` (hoặc dùng ảnh được truyền vào) và đọc ảnh.
2. Áp dụng bộ lọc 1D theo chiều ngang với ma trận lọc trung bình kích thước `1x5`.
3. Áp dụng bộ lọc 1D theo chiều ngang với ma trận lọc có trọng số `1 2 4 2 1`.
4. Xoay hai ma trận lọc 1D ở trên sang chiều dọc (`5x1`) rồi áp dụng lọc theo cột.
5. Áp dụng bộ lọc 2D với hai ma trận lọc `3x3`:

- Ma trận lọc trung bình (`ones(3x3)/9`)
- Ma trận lọc có trọng số `[[1,2,1],[2,8,2],[1,2,1]]/20`

Tất cả kết quả được lưu thành file ảnh riêng trong thư mục `outputs/`.

## Clean Architecture

- `src/domain`: abstraction và model nghiệp vụ (`FilterEngine`, `Kernel`, `KernelFactory`).
- `src/application`: use-case điều phối toàn bộ pipeline.
- `src/infrastructure`: adapter cho OpenCV (`filter2D`), IO ảnh, tìm/chọn ảnh trong workspace.
- `main.py`: entrypoint CLI, dependency wiring.

## Quick Start

1. Cài dependency:

```bash
pip install -r requirements.txt
```

2. Bỏ một hoặc nhiều ảnh vào thư mục `assets/`, sau đó chạy ngẫu nhiên:

```bash
python main.py
```

3. Chạy với ảnh cụ thể:

```bash
python main.py --input ../basic_image_processing/assets/sample.jpg
```

4. Chạy với seed cố định để tái lập kết quả chọn ảnh ngẫu nhiên:

```bash
python main.py --seed 42
```

5. Tắt hiển thị cửa sổ ảnh trong quá trình xử lý (dùng khi chạy môi trường không có GUI):

```bash
python main.py --no-show
```

## Output Files

Trong `outputs/` sẽ có:

- `01_original_color.png`
- `02_1d_mean_1x5_horizontal.png`
- `03_1d_weighted_1x5_horizontal.png`
- `04_1d_mean_5x1_vertical.png`
- `05_1d_weighted_5x1_vertical.png`
- `06_2d_mean_3x3.png`
- `07_2d_weighted_3x3.png`
- `run_summary.txt`

File `run_summary.txt` ghi lại ảnh đầu vào được chọn và thông tin ma trận lọc đã dùng.

## Cau 2 - Canny Edge Detection va Masking

### Lua chon phuong phap

De giu chi tiet bien trong khi van lam mo nhieu toan cuc, giai phap duoc chon la **Canny Edge Detection + Masking**.

- Y tuong:
  1. Tim bien bang Canny tren anh xam.
  2. Tao anh mo toan cuc bang Gaussian Blur.
  3. Dung mat na bien: vung bien giu anh goc, vung con lai lay anh mo.

### Chay demo Cau 2

```bash
python question2_main.py --no-show
```

Hoac chi dinh anh cu the:

```bash
python question2_main.py --input ../basic_image_processing/assets/sample.jpg --no-show
```

### Ket qua sinh ra

Trong `outputs_question2/` se co:

- `01_original.png`: anh goc
- `02_blurred.png`: anh mo toan cuc bang Gaussian
- `03_canny_mask.png`: mat na bien tu Canny
- `04_edge_preserved_result.png`: ket qua ghep theo mat na bien
- `05_comparison_panel.png`: anh ghep ngang de so sanh nhanh
- `run_summary_question2.txt`: tom tat phuong phap va tham so
