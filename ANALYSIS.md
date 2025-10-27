# PHÂN TÍCH DỰ ÁN VOPAK ALERT

**Ngày cập nhật:** 27/10/2024  
**Phiên bản:** 1.0  
**Trạng thái:** Production Ready

---

## 📋 TỔNG QUAN DỰ ÁN

Vopak Alert là ứng dụng giám sát tự động hệ thống Vopak với giao diện đồ họa Tkinter, được thiết kế để:
- Giám sát 3 hệ thống quan trọng của Vopak
- Tự động phát hiện sự cố
- Gửi cảnh báo qua email
- Có thể lên lịch theo thời gian thực

---

## 🏗️ CẤU TRÚC PROJECT

```
vopakalert/
├── main.py              # Ứng dụng chính (GUI với Tkinter)
├── lib.py               # Functions xử lý logic giám sát
├── main.spec            # Cấu hình PyInstaller
├── build.py             # Script build cross-platform (Python)
├── build.sh             # Script build cho macOS/Linux (Bash)
├── build.ps1            # Script build cho Windows (PowerShell)
├── README.md            # Tài liệu hướng dẫn
├── ANALYSIS.md          # File phân tích này
├── .gitignore           # Git ignore rules
├── build/               # Thư mục tạm PyInstaller
└── dist/                # Output file .exe/.app
    └── main_[epoch]     # Executable có timestamp
```

---

## 🔍 PHÂN TÍCH CHI TIẾT FILE

### 1. FILE `lib.py` (150 dòng)

#### `get_epoch_range(days_ahead=5)` (dòng 11-18)
**Mục đích:** Tính toán khoảng thời gian epoch để query API Boiler Activity

**Input:**
- `days_ahead`: Số ngày tương lai muốn lấy data (mặc định 5)

**Output:**
- `start_epoch`: Epoch time (milliseconds) từ hôm qua 00:00:00
- `end_epoch`: Epoch time (milliseconds) đến ngày +days_ahead 00:00:00

**Logic:**
```python
current_day = datetime.now() với h=0, m=0, s=0
start_day = current_day - 1 day
end_day = current_day + days_ahead
start_epoch = timestamp(start_day) * 1000 (ms)
end_epoch = timestamp(end_day) * 1000 (ms)
```

---

#### `send_email_alert(alert_type)` (dòng 21-54)
**Mục đích:** Gửi email cảnh báo khi phát hiện sự cố

**Parameters:**
- `alert_type`: Loại cảnh báo
  - `"recommendation"`: Vấn đề Boiler Activity data
  - `"opcdie"`: OPC data không có notifications mới
  - `"webdie"` (mặc định): Website production down

**Thông tin gửi email:**
- **From:** luanxinhdata@gmail.com
- **To:** lutran@atomiton.com, ktran@atomiton.com, ltran@atomiton.com
- **SMTP:** smtp.gmail.com:465 (SSL)
- **Password:** App Password (lưu trong code - KHÔNG BẢO MẬT)

**Security Note:** ⚠️ Password đang hardcode trong code - cần chuyển sang environment variables

---

#### `check_recommendation()` (dòng 56-85)
**Mục đích:** Kiểm tra Boiler Activity data từ API

**Endpoint:** `http://vopakext.atomiton.com:8090/fid-vopaksteamact`

**Payload:**
```python
eval = GetBoilerActivityDetails(start_epoch, end_epoch, 5, 0)
```

**Headers:**
- `UserToken`: SuperUser
- `Content-Type`: text/plain

**Logic:**
1. Lấy epoch range (5 ngày)
2. POST request đến API
3. Parse JSON response
4. Kiểm tra `totalRecords < 5`
5. Nếu < 5 → Gửi email cảnh báo "recommendation"

**Error Handling:**
- Bắt lỗi JSON parsing
- Log raw response nếu lỗi

---

#### `check_production_status()` (dòng 87-97)
**Mục đích:** Kiểm tra trang production còn hoạt động không

**Endpoint:** `http://bwcext.atomiton.com:8090/fid-tqlengineres/vopakui/index.html#/auth/login`

**Logic:**
1. GET request với timeout 10s
2. Kiểm tra `response.status_code == 200`
3. Nếu không 200 → Gửi cảnh báo "webdie"
4. Exception → Gửi cảnh báo "webdie"

**Error Cases:**
- Connection timeout
- HTTP status != 200
- Website unreachable

---

#### `check_OPC_data()` (dòng 99-150)
**Mục đích:** Kiểm tra OPC Notifications (Alert XML) có data mới trong ngày

**Endpoint:** `http://vopakext.atomiton.com:8080/fid-DigitalTerminalInterface`

**Payload:** XML Query
```xml
<Query>
  <Find limit="10" offset="0" orderBy="Notification.time desc">
    <Notification>
      <alertText ne=""/>
    </Notification>
  </Find>
</Query>
```

**Headers:**
- `userToken`: SuperUser
- `Content-Type`: application/xml

**Logic:**
1. POST XML payload
2. Parse XML response
3. Lọc notifications có `alertText != ""`
4. Check notifications hôm nay (UTC timezone)
5. Nếu **KHÔNG CÓ** notification hôm nay → Gửi cảnh báo "opcdie"

**Error Handling:**
- Bắt Exception từ requests
- Validate HTTP status code
- Parse XML với error handling
- Handle timezone conversion (UTC)

---

### 2. FILE `main.py` (165 dòng)

#### Global Variables (dòng 16)
```python
running = False  # Cờ điều khiển Start/Stop scheduler
```

#### `log_message(msg)` (dòng 19-25)
**Mục đích:** Hiển thị log với timestamp vào Text widget

**Features:**
- Timestamp format: HH:MM:SS
- Auto-scroll to bottom
- Disabled text widget để tránh edit

---

#### `run_scheduler()` (dòng 28-34)
**Mục đích:** Thread chạy scheduler trong background

**Logic:**
1. Loop while `running == True`
2. Chạy `schedule.run_pending()` mỗi giây
3. Check `running` flag
4. Stop khi `running = False`

**Note:** Daemon thread - auto kill khi app exit

---

#### `start_app()` (dòng 37-86)
**Mục đích:** Khởi động tất cả scheduled tasks

**Logic Flow:**
1. Set `running = True`
2. Clear all previous schedules
3. **Check Validation:** Đọc interval từ entry widgets
   - Check `interval > 0`
   - Show error nếu không hợp lệ
4. **Setup Schedules:**
   - Nếu `var_recommend` checked → `schedule.every(X).minutes.do(check_recommendation)`
   - Nếu `var_production` checked → `schedule.every(Y).minutes.do(check_production_status)`
   - Nếu `var_opc` checked → `schedule.every(Z).minutes.do(check_OPC_data)`
5. **Validate:** Phải chọn ít nhất 1 task
6. **Start Thread:** Spawn background scheduler thread
7. **Update UI:** Disable Start button, Enable Stop button

**Default Intervals:**
- Recommendation: 5 phút
- Production: 10 phút
- OPC: 3 phút

---

#### `safe_run(func, name)` (dòng 88-95)
**Mục đích:** Wrapper chạy function an toàn với error handling

**Features:**
- Try-catch để bắt exception
- Log khi bắt đầu và kết thúc
- Log error nếu có exception
- Không crash app khi task lỗi

---

#### `stop_app()` (dòng 98-105)
**Mục đích:** Dừng tất cả scheduled tasks

**Logic:**
1. Set `running = False`
2. Clear all schedules
3. Update UI buttons
4. Log stop message

---

#### UI Components (dòng 108-164)
**Window:**
- Title: "Vopak Monitor"
- Size: 600x400
- Root: Tk

**Frame Structure:**
```
root
└── frame (padding=15)
    ├── Title Label
    ├── Task Selection (3 checkboxes)
    │   ├── Recommendation (5 min)
    │   ├── Production (10 min)
    │   └── OPC (3 min)
    ├── Buttons (Start/Stop)
    └── Log Area (Text widget)
```

**Task Selection:**
- Checkbox + Entry widget cho mỗi task
- Validation input là số nguyên > 0
- UI layout với side='left' packing

**Buttons:**
- Start: `btn_start` - Start App ▶️
- Stop: `btn_stop` - Stop App 🛑 (disabled ban đầu)

**Log Area:**
- Text widget với wrap='word'
- Height: 10 lines
- Background: #f4f4f4
- Disabled state để prevent edit
- Show logs với timestamp

---

### 3. BUILD CONFIGURATION

#### `main.spec` (PyInstaller config)
**Target:** Windows executable (.exe)
**Mode:** One-file executable
**Console:** No (windowed mode)
**UPX:** Yes (compression enabled)

**Note:** Spec file này config cho Windows, nhưng PyInstaller sẽ tự động adapt cho macOS/Linux khi chạy

---

## 🔨 BUILD PROCESS

### Build Scripts

#### 1. `build.py` (Python - Cross-platform)
**Features:**
- ✅ Tự động detect OS
- ✅ Cài PyInstaller nếu thiếu
- ✅ Generate timestamp cho filename
- ✅ Error handling đầy đủ
- ✅ Clean builds cũ
- ✅ Cross-platform executable name

**Command:**
```bash
python3 build.py
```

**Output:**
- macOS: `dist/main_1761548123`
- Windows: `dist/main_1761548123.exe`

---

#### 2. `build.sh` (Bash - macOS/Linux)
**Features:**
- ✅ Colored output
- ✅ Timestamp filename
- ✅ File info display
- ✅ Cross-platform detection

**Command:**
```bash
chmod +x build.sh
./build.sh
```

---

#### 3. `build.ps1` (PowerShell - Windows)
**Features:**
- ✅ Windows-specific
- ✅ Timestamp filename
- ✅ Colored output

**Command:**
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Build Limitations
1. **KHÔNG CÓ cross-compilation:** Phải build trên OS target
   - Build trên macOS → macOS executable only
   - Build trên Windows → Windows .exe only
   - Không thể build Windows .exe từ macOS

2. **Windows Build Options:**
   - Build trực tiếp trên Windows
   - Dùng Windows VM trên macOS
   - Sử dụng GitHub Actions

### Security Issues
1. **⚠️ Hardcoded Email Credentials:**
   - Password trong code: `lib.py:38`
   - **Recommend:** Sử dụng environment variables

2. **⚠️ Email App Password:**
   - Current: `xryl xwzy gdnq benp`
   - **Recommend:** Rotate periodically

### Known Issues
1. **Tkinter trên macOS:**
   - Warning khi build: "tkinter installation is broken"
   - Executable vẫn chạy nhưng GUI có thể buggy
   - **Solution:** Test kỹ trước khi deploy

2. **Missing Log File:**
   - Hiện tại chỉ log ra UI
   - **Recommend:** Thêm file logging

3. **No Persistence:**
   - Settings không lưu giữa sessions
   - **Recommend:** Lưu cấu hình ra file

---

## 📊 DEPENDENCIES

### Python Dependencies
```python
requests        # HTTP requests cho API calls
schedule        # Task scheduling
tkinter         # GUI framework (built-in)
smtplib         # Email sending (built-in)
email           # Email formatting (built-in)
datetime        # Time handling (built-in)
threading       # Background tasks (built-in)
```

### Build Dependencies
```bash
pyinstaller     # Packaging tool
```

---

## 🚀 USAGE GUIDE

### Running from Source
```bash
# Install dependencies
pip install requests schedule

# Run app
python main.py
```

### Building Executable

#### Option 1: Python Script (Recommended)
```bash
python3 build.py
```
Output: `dist/main_[epoch]`

#### Option 2: Bash Script (macOS/Linux)
```bash
./build.sh
```

#### Option 3: PowerShell (Windows)
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

### Building for Windows from macOS
**Không thể trực tiếp.** Options:
1. **Virtual Machine:** Parallels/VMware
2. **CI/CD:** GitHub Actions
3. **Remote Build:** Windows machine access

---

## 🧪 TESTING

### Manual Testing
1. Run app: `python main.py`
2. Select tasks to monitor
3. Set intervals
4. Click Start
5. Check logs
6. Verify email alerts work

### Build Testing
1. Run build script
2. Check executable exists
3. Verify file size reasonable
4. Test executable on target OS
5. Verify all 3 monitoring functions work

---

## 📝 TODO / IMPROVEMENTS

### High Priority
- [ ] Remove hardcoded email password → use env vars
- [ ] Add file logging (not just UI)
- [ ] Save user settings between sessions
- [ ] Add icon for executable

### Medium Priority
- [ ] Add health check cho SMTP connection
- [ ] Validate interval inputs (min/max constraints)
- [ ] Add "Clear Logs" button
- [ ] Add export logs to file

### Low Priority
- [ ] Add database để lưu history
- [ ] Add config file cho endpoints
- [ ] Add unit tests
- [ ] Add CI/CD pipeline

---

## 🔗 API ENDPOINTS

### 1. Boiler Activity API
```
URL: http://vopakext.atomiton.com:8090/fid-vopaksteamact
Method: POST
Headers:
  - UserToken: SuperUser
  - Content-Type: text/plain
Body: eval = GetBoilerActivityDetails(start, end, 5, 0)
```

### 2. Production Status API
```
URL: http://bwcext.atomiton.com:8090/fid-tqlengineres/vopakui/index.html#/auth/login
Method: GET
Timeout: 10 seconds
```

### 3. OPC Data API
```
URL: http://vopakext.atomiton.com:8080/fid-DigitalTerminalInterface
Method: POST
Headers:
  - userToken: SuperUser
  - Content-Type: application/xml
Body: <Query><Find limit="10"...>
```

---

## 📞 SUPPORT

- **Email Recipients:** lutran@atomiton.com, ktran@atomiton.com, ltran@atomiton.com
- **Sender:** luanxinhdata@gmail.com

---

## 📄 VERSION HISTORY

- **v1.0 (2024):** Initial release
  - 3 monitoring functions
  - GUI interface
  - Email alerts
  - Build scripts với timestamp

---

**End of Analysis**
