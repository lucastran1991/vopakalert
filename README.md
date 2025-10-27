# Vopak Alert Monitor

Ứng dụng giám sát tự động cho hệ thống Vopak với giao diện đồ họa.

## 📋 Chức năng

- **Check Recommendation**: Giám sát dữ liệu Boiler Activity
- **Check Production Status**: Kiểm tra trạng thái trang production
- **Check OPC Data**: Theo dõi thông báo OPC realtime
- **Email Alerts**: Tự động gửi cảnh báo qua email khi phát hiện sự cố

## 🛠️ Cài đặt

### Yêu cầu

- Python 3.7+
- pip

### Quick Install

#### Method 1: Automated Script (Recommended)

**macOS/Linux:**
```bash
./install.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

#### Method 2: Manual Install

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually
pip install requests schedule
```

## 🚀 Chạy ứng dụng

### Chạy từ source code

```bash
python main.py
```

### Build thành file exe

Có 3 cách để build:

#### 1. Sử dụng script bash (macOS/Linux)

```bash
chmod +x build.sh
./build.sh
```

#### 2. Sử dụng Python script (Cross-platform)

```bash
python build.py
```

#### 3. Sử dụng PowerShell script (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

#### 4. Build thủ công với PyInstaller

```bash
pyinstaller main.spec
```

## 📦 Cấu trúc project

```
vopakalert/
├── main.py              # File chính (GUI)
├── lib.py               # Functions xử lý logic
├── requirements.txt     # Python dependencies
├── install.sh           # Install script (macOS/Linux)
├── install.ps1          # Install script (Windows)
├── main.spec            # Cấu hình PyInstaller
├── build.sh             # Build script (bash)
├── build.py             # Build script (Python)
├── build.ps1            # Build script (PowerShell)
├── dist/                # File exe sau khi build
│   └── *.app or *.exe
└── README.md
```

## 📧 Email Alerts

Ứng dụng tự động gửi email cảnh báo đến:
- lutran@atomiton.com
- ktran@atomiton.com
- ltran@atomiton.com

Khi phát hiện:
- Recommendation data < 5 records
- Production website down
- OPC data không có thông báo mới trong ngày

## 🔧 Cấu hình

Trong giao diện, bạn có thể:
- Chọn các task cần chạy
- Đặt khoảng thời gian kiểm tra (phút)
- Xem logs realtime
- Start/Stop scheduler

## 📝 Logs

Tất cả hoạt động được log ra giao diện với timestamp.

## ⚠️ Lưu ý

- Cần kết nối internet để gửi email
- Các API endpoints cần accessible
- Email credentials được hardcode trong code (nên chuyển sang environment variables trong production)

## 📚 Additional Documentation

- **[ANALYSIS.md](ANALYSIS.md)** - Chi tiết phân tích function
- **[BUILD_MACOS.md](BUILD_MACOS.md)** - Hướng dẫn build macOS app
- **[QUICK_START_MACOS.md](QUICK_START_MACOS.md)** - Quick start cho macOS
- **[EMAIL_TOGGLE_SUMMARY.md](EMAIL_TOGGLE_SUMMARY.md)** - Chi tiết email toggle feature

## 📖 Phân tích chi tiết

Xem file [ANALYSIS.md](ANALYSIS.md) để hiểu rõ:
- Chi tiết từng function
- Logic flow của application
- Build process
- Security concerns
- API endpoints
- Improvements và TODO

## 📄 License

Internal use - Atomiton Inc.
