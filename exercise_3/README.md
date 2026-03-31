# Exercise 3 - Edge, Line, and Circle Detection

Bai tap nay tach ro thanh 3 yeu cau rieng tren cung mot anh dau vao:

1. Ve duong bao (xoc canh vien doi tuong) voi Canny + contour.
2. Tim tat ca cac doan thang co the va loc doan qua ngan, qua gan nhau.
3. Tim tat ca cac hinh tron va loc duong tron qua lon, qua be, qua gan nhau.

## Cau truc thu muc

```bash
exercise_3/
├── assets/
├── docs/
│   └── sources.txt
├── outputs/
│   ├── edge/
│   ├── lines/
│   └── circles/
├── src/
│   ├── application/
│   │   ├── edge_detection_use_case.py
│   │   ├── line_detection_use_case.py
│   │   └── circle_detection_use_case.py
│   └── infrastructure/
│       ├── image_io.py
│       └── workspace_image_provider.py
├── main.py
└── requirements.txt
```

## Cai dat

```bash
pip install -r requirements.txt
```

## Su dung

Dat it nhat 1 anh vao `assets/`, sau do chay:

```bash
python main.py
```

Neu muon chi dinh anh cu the:

```bash
python main.py --input assets/sample.jpg
```

Tat hien thi cua so (phu hop khi chay khong GUI):

```bash
python main.py --no-show
```

## Cach dap ung de bai

### Yeu cau 1 - Edge/Contour

- `src/application/edge_detection_use_case.py`
- Su dung 2 profile tham so khac nhau:
  - Profile 1: blur kernel nho + Canny threshold thap.
  - Profile 2: blur kernel lon hon + Canny threshold cao hon.
- Ket qua luu trong `outputs/edge/`.

### Yeu cau 2 - Line Detection

- `src/application/line_detection_use_case.py`
- Su dung HoughLinesP:
  - Profile 1: de phat hien nhieu line ung vien.
  - Profile 2: tang `minLineLength`, dieu chinh `threshold` va `maxLineGap`.
- Bo sung buoc loc khoang cach tam line (`min_center_distance_profile_2`) de giam line qua gan nhau.
- Ket qua luu trong `outputs/lines/`.

### Yeu cau 3 - Circle Detection

- `src/application/circle_detection_use_case.py`
- Su dung HoughCircles:
  - Profile 1: tim nhieu ung vien hinh tron.
  - Profile 2: tang `minDist`, dat `minRadius/maxRadius`, dieu chinh `param2`.
- Muc dich: loai bo tron qua lon, qua be va qua sat nhau.
- Ket qua luu trong `outputs/circles/`.

Moi thu muc output deu co `run_summary_*.txt` de ghi lai tham so va so luong doi tuong tim duoc.
