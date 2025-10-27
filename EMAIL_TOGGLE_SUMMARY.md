# Email Toggle Feature Summary

## 📧 Email Toggle Added to UI

### Changes Made:

### 1. **main.py Updates**

#### Global Variable Added:
```python
email_enabled = True  # Cờ bật/tắt gửi email
```

#### New Functions:
- `safe_send_email(alert_type)` - Wrapper to check email enabled flag
- `toggle_email()` - Toggle email alerts and update checkbox color

#### Email Toggle Section:
- Added checkbox: "📧 Enable Email Alerts"
- Green when enabled, Red when disabled
- Helper text: "(Toggle to enable/disable email notifications)"

#### Schedule Integration:
- All scheduled tasks now pass `isNotify=email_enabled` parameter
- Email alerts only sent when checkbox is checked

### 2. **UI Layout:**

```
Window Layout:
├── Monitoring Tasks (LabelFrame)
│   ├── Check Recommendation [5] min
│   ├── Check Production Status [10] min
│   └── Check OPC Data [3] min
│
├── 📧 Enable Email Alerts (Checkbox)
│   [Green when enabled / Red when disabled]
│
├── Control Buttons
│   ├── ▶️ Start App
│   └── 🛑 Stop App
│
└── Activity Logs (with scrollbar)
```

### 3. **How It Works:**

1. **Checkbox Interaction:**
   - Click checkbox to toggle
   - Visual feedback: Green = enabled, Red = disabled
   - Log message displayed when toggled

2. **Email Sending Logic:**
   - When enabled: Emails sent normally
   - When disabled: Monitoring still works, but no emails sent
   - Log shows "📧 Email disabled - skipping alert"

3. **Dynamic Control:**
   - Can be toggled at any time
   - State persists during session
   - Default: Enabled

### 4. **Integration with lib.py:**

All three monitoring functions in `lib.py` already have `isNotify` parameter:
- `check_recommendation(isNotify=True)`
- `check_production_status(isNotify=True)`
- `check_OPC_data(isNotify=True)`

main.py now passes the `email_enabled` flag to control notifications.

### 5. **Usage:**

**Enable Email Alerts:**
- Check the checkbox
- Checkbox turns green
- Email alerts will be sent when issues detected

**Disable Email Alerts:**
- Uncheck the checkbox
- Checkbox turns red
- No emails sent (but monitoring continues)

### 6. **Benefits:**

✅ Users can control email notifications
✅ Reduce email spam during testing
✅ Easy to disable if SMTP issues occur
✅ Visual feedback for current state
✅ Non-intrusive toggle

### 7. **Log Messages:**

**When enabled:**
```
📧 Email alerts enabled
📧 Email alert sent: recommendation
```

**When disabled:**
```
📧 Email alerts disabled
📧 Email disabled - skipping alert: recommendation
```

---

**Status:** ✅ Complete
**Default State:** Email alerts enabled
**Location:** Between task selection and control buttons
