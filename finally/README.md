# Hệ Thống Giám Sát và Nhắc Nhở Tư Thế Ngồi

> Ứng dụng thị giác máy tính giám sát tư thế ngồi theo thời gian thực, cảnh báo khi ngồi sai và gửi thông báo qua Telegram.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Giới Thiệu

Hệ thống sử dụng **MediaPipe Pose** và **OpenCV** để phát hiện tư thế ngồi qua webcam đặt bên hông. Phân tích góc nghiêng cổ và lưng theo thời gian thực, cảnh báo đa kênh khi phát hiện tư thế xấu.

### Tính Năng

- Phát hiện tư thế ngồi real-time qua webcam hoặc video
- Phân loại tốt/xấu dựa trên góc nghiêng cổ (< 25°) và lưng (< 10°)
- Cảnh báo âm thanh khi ngồi sai quá 15 giây
- Tự động chụp ảnh tư thế xấu
- Gửi cảnh báo qua Telegram Bot
- Báo cáo thống kê cuối phiên với biểu đồ
- Giao diện trực quan: bộ xương, thanh đo, nhãn trạng thái

---

## Kiến Trúc

Thiết kế theo **OOP** và nguyên tắc **SOLID** — mỗi class một trách nhiệm duy nhất.

```
finally/
├── main.py                        # PostureMonitor — điều phối hệ thống
├── config.py                      # Cấu hình (ngưỡng, Telegram, màu sắc)
├── core/
│   ├── pose_detector.py           # PoseDetector — bọc MediaPipe Pose
│   ├── posture_analyzer.py        # PostureAnalyzer + PostureResult
│   └── session_tracker.py         # SessionTracker — đếm frame, thống kê
├── services/
│   ├── alert_service.py           # AlertService — beep cảnh báo
│   ├── screenshot_service.py      # ScreenshotService — chụp ảnh tự động
│   ├── telegram_service.py        # TelegramService — gửi Telegram
│   └── report_service.py          # ReportService — biểu đồ matplotlib
├── ui/
│   └── overlay_renderer.py        # OverlayRenderer — vẽ giao diện camera
├── generate_report.py             # Tạo báo cáo Word (.docx)
└── screenshots/                   # Ảnh chụp + biểu đồ phiên
```

---

## Cài Đặt

### Yêu cầu

- Python 3.10+
- Webcam (đặt bên hông)
- Windows (sử dụng `winsound` cho cảnh báo âm thanh)

### Cài thư viện

```bash
pip install mediapipe opencv-contrib-python matplotlib requests python-docx
```

---

## Sử Dụng

### Chạy cơ bản

```bash
python main.py
```

### Tùy chọn dòng lệnh

```bash
# Cảnh báo sau 5 giây (mặc định 15)
python main.py --alert-time 5

# Dùng file video thay webcam
python main.py --video video.mp4
```

### Thoát

Nhấn **`q`** trên cửa sổ camera. Hệ thống tự động:
- In thống kê phiên ra terminal
- Tạo biểu đồ `screenshots/session_report.png`
- Gửi báo cáo qua Telegram (nếu đã cấu hình)

---

## Cấu Hình Telegram

1. Mở Telegram → tìm **@BotFather** → gửi `/newbot` → lấy **token**
2. Tìm **@userinfobot** → gửi `/start` → lấy **chat_id**
3. Mở `config.py` và điền:

```python
TELEGRAM_BOT_TOKEN = "your_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"
```

---

## Cách Đặt Camera

```
         [Màn hình]
            |
     ┌──────┴──────┐
     │   Người     │
     │   ngồi      │
     └──────┬──────┘
            │
    Camera (bên hông, ngang tầm vai, cách 1-1.5m)
```

> **Lưu ý:** Camera **phải đặt ở bên hông** (side view). Nếu đặt phía trước, hệ thống sẽ cảnh báo "Vai không thẳng hàng".

---

## Cấu Hình Ngưỡng

Chỉnh trong `config.py`:

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| `NECK_ANGLE_THRESHOLD` | 25° | Góc nghiêng cổ tối đa |
| `TORSO_ANGLE_THRESHOLD` | 10° | Góc nghiêng lưng tối đa |
| `ALERT_TIME` | 15s | Thời gian ngồi sai trước khi cảnh báo |
| `ALERT_SOUND_COOLDOWN` | 5s | Khoảng nghỉ giữa 2 lần beep |
| `SCREENSHOT_COOLDOWN` | 30s | Khoảng nghỉ giữa 2 lần chụp ảnh |
| `TELEGRAM_COOLDOWN` | 60s | Khoảng nghỉ giữa 2 lần gửi Telegram |

---

## Kết Quả Demo

| Thông số | Giá trị |
|----------|---------|
| Thời lượng phiên | 65 giây |
| Tư thế tốt | 34,0% (298 khung hình) |
| Tư thế xấu | 66,0% (578 khung hình) |
| Số lần cảnh báo | 2 |
| Ảnh chụp tự động | 2 |
| Tốc độ xử lý | ~13 hình/giây (CPU) |

---

## Công Nghệ

| Thư viện | Phiên bản | Vai trò |
|----------|-----------|---------|
| [MediaPipe](https://ai.google.dev/edge/mediapipe) | 0.10+ | Phát hiện điểm mốc cơ thể |
| [OpenCV](https://opencv.org/) | 4.x | Xử lý ảnh, giao diện camera |
| [matplotlib](https://matplotlib.org/) | 3.x | Biểu đồ báo cáo |
| [requests](https://docs.python-requests.org/) | 2.x | Gửi HTTP đến Telegram API |
| [python-docx](https://python-docx.readthedocs.io/) | 1.x | Tạo báo cáo Word |

---

## Tài Liệu Tham Khảo

- [MediaPipe Pose Documentation](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker)
- [BlazePose Paper (arXiv:2006.10204)](https://arxiv.org/abs/2006.10204)
- [LearnOpenCV — Body Posture Analysis](https://learnopencv.com/building-a-body-posture-analysis-system-using-mediapipe/)

---

## License

MIT License — xem file [LICENSE](LICENSE) để biết thêm chi tiết.
