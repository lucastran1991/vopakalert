import requests
import json
from datetime import datetime, timedelta
from lib import get_epoch_range
from lib import send_email_alert
from lib import check_recommendation
from lib import check_production_status
from lib import check_OPC_data
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import schedule


running = False  # Cờ điều khiển chạy / dừng
email_enabled = True  # Cờ bật/tắt gửi email


def log_message(msg, is_error=False):
    """Ghi log ra Text box với tùy chọn màu đỏ cho lỗi"""
    # Shorten message if too long (max 80 chars for display)
    display_msg = msg
    if len(msg) > 80:
        display_msg = msg[:77] + "..."
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_box.config(state='normal')
    
    # Insert timestamp in normal color
    log_box.insert(tk.END, f"[{timestamp}] ", "timestamp")
    
    # Insert message with color based on error status
    if is_error:
        log_box.insert(tk.END, f"{display_msg}\n", "error")
    else:
        log_box.insert(tk.END, f"{display_msg}\n", "normal")
    
    log_box.see(tk.END)
    log_box.config(state='disabled')


def run_scheduler():
    """Thread chạy schedule"""
    global running
    while running:
        schedule.run_pending()
        time.sleep(1)
    log_message("🛑 Scheduler stopped.")


def start_app():
    """Bắt đầu chạy task"""
    global running
    running = True
    schedule.clear()

    # Lấy interval cho từng task
    try:
        if var_recommend.get():
            interval_rec = int(entry_recommend.get())
            if interval_rec <= 0:
                raise ValueError
            schedule.every(interval_rec).minutes.do(
                lambda: safe_run(lambda: check_recommendation(isNotify=email_enabled), "Check Recommendation")
            )
            log_message(f"✅ Scheduled: check_recommendation() every {interval_rec} minutes")

        if var_production.get():
            interval_prod = int(entry_production.get())
            if interval_prod <= 0:
                raise ValueError
            schedule.every(interval_prod).minutes.do(
                lambda: safe_run(lambda: check_production_status(isNotify=email_enabled), "Check Production Status")
            )
            log_message(f"✅ Scheduled: check_production_status() every {interval_prod} minutes")

        if var_opc.get():
            interval_opc = int(entry_opc.get())
            if interval_opc <= 0:
                raise ValueError
            schedule.every(interval_opc).minutes.do(
                lambda: safe_run(lambda: check_OPC_data(isNotify=email_enabled), "Check OPC Data")
            )
            log_message(f"✅ Scheduled: check_OPC_data() every {interval_opc} minutes")

    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive numbers for minutes.")
        return

    if not (var_recommend.get() or var_production.get() or var_opc.get()):
        messagebox.showwarning("Warning", "Please select at least one task.")
        return

    # Cập nhật nút Start/Stop
    btn_start.config(state="disabled")
    btn_stop.config(state="normal")
    
    # Disable all checkboxes while running
    checkbox_recommend.config(state="disabled")
    checkbox_production.config(state="disabled")
    checkbox_opc.config(state="disabled")
    
    # Disable email checkbox
    checkbox_email.config(state="disabled")
    
    # Disable all entry fields
    entry_recommend.config(state="disabled")
    entry_production.config(state="disabled")
    entry_opc.config(state="disabled")

    log_message("▶️ Scheduler started.")
    threading.Thread(target=run_scheduler, daemon=True).start()


def safe_run(func, name):
    """Chạy hàm an toàn, có log"""
    try:
        log_message(f"Running: {name}() ...")
        func()
        log_message(f"✅ Finished: {name}()")
    except Exception as e:
        log_message(f"❌ Error in {name}(): {e}", is_error=True)


def safe_send_email(alert_type):
    """Gửi email an toàn, chỉ gửi nếu enabled"""
    global email_enabled
    if email_enabled:
        try:
            send_email_alert(alert_type)
            log_message(f"📧 Email alert sent: {alert_type}")
        except Exception as e:
            log_message(f"❌ Email failed: {e}", is_error=True)
    else:
        log_message(f"📧 Email disabled - skipping alert: {alert_type}")


def toggle_email():
    """Toggle email alerts"""
    global email_enabled
    email_enabled = var_email_enabled.get()
    status = "enabled" if email_enabled else "disabled"
    log_message(f"📧 Email alerts {status}")
    # Update button appearance using ttk.Style
    if email_enabled:
        style.configure('EmailEnabled.TCheckbutton', foreground='green')
        checkbox_email.config(style='EmailEnabled.TCheckbutton')
    else:
        style.configure('EmailDisabled.TCheckbutton', foreground='gray')
        checkbox_email.config(style='EmailDisabled.TCheckbutton')


def stop_app():
    """Dừng toàn bộ task"""
    global running
    running = False
    schedule.clear()
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")
    
    # Enable all checkboxes after stopping
    checkbox_recommend.config(state="normal")
    checkbox_production.config(state="normal")
    checkbox_opc.config(state="normal")
    
    # Enable email checkbox
    checkbox_email.config(state="normal")
    
    # Enable all entry fields
    entry_recommend.config(state="normal")
    entry_production.config(state="normal")
    entry_opc.config(state="normal")
    
    log_message("🛑 Stopping all scheduled tasks...")


# ------------------ UI ------------------
root = tk.Tk()
root.title("Vopak Monitor")
root.geometry("650x450")

# Configure ttk styles
style = ttk.Style()
style.configure('EmailEnabled.TCheckbutton', foreground='green')
style.configure('EmailDisabled.TCheckbutton', foreground='gray')

# Main frame with padding
frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill='both')

# --- Task selection section ---
section_tasks = ttk.LabelFrame(frame, text="Monitoring Tasks", padding=15)
section_tasks.pack(fill='x', pady=(0, 15))

ttk.Label(section_tasks, text="Select tasks and frequency (minutes):", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 10))

# Task 1 - Recommendation
var_recommend = tk.BooleanVar()
frame_rec = ttk.Frame(section_tasks)
frame_rec.pack(anchor='w', pady=5, fill='x')
checkbox_recommend = ttk.Checkbutton(frame_rec, text="Check Recommendation", variable=var_recommend, width=25)
checkbox_recommend.pack(side='left')
ttk.Label(frame_rec, text="Every").pack(side='left', padx=(10, 5))
entry_recommend = ttk.Entry(frame_rec, width=6, justify='center')
entry_recommend.insert(0, "5")
entry_recommend.pack(side='left')
ttk.Label(frame_rec, text="min").pack(side='left', padx=(5, 0))

# Task 2 - Production
var_production = tk.BooleanVar()
frame_prod = ttk.Frame(section_tasks)
frame_prod.pack(anchor='w', pady=5, fill='x')
checkbox_production = ttk.Checkbutton(frame_prod, text="Check Production Status", variable=var_production, width=25)
checkbox_production.pack(side='left')
ttk.Label(frame_prod, text="Every").pack(side='left', padx=(10, 5))
entry_production = ttk.Entry(frame_prod, width=6, justify='center')
entry_production.insert(0, "10")
entry_production.pack(side='left')
ttk.Label(frame_prod, text="min").pack(side='left', padx=(5, 0))

# Task 3 - OPC
var_opc = tk.BooleanVar()
frame_opc = ttk.Frame(section_tasks)
frame_opc.pack(anchor='w', pady=5, fill='x')
checkbox_opc = ttk.Checkbutton(frame_opc, text="Check OPC Data", variable=var_opc, width=25)
checkbox_opc.pack(side='left')
ttk.Label(frame_opc, text="Every").pack(side='left', padx=(10, 5))
entry_opc = ttk.Entry(frame_opc, width=6, justify='center')
entry_opc.insert(0, "3")
entry_opc.pack(side='left')
ttk.Label(frame_opc, text="min").pack(side='left', padx=(5, 0))

# --- Email toggle section ---
section_email = ttk.Frame(frame)
section_email.pack(pady=(0, 10))

var_email_enabled = tk.BooleanVar()
var_email_enabled.set(True)  # Default enabled
checkbox_email = ttk.Checkbutton(section_email, text="📧 Enable Email Alerts", variable=var_email_enabled, command=toggle_email)
checkbox_email.pack(side='left')
# Set initial style to enabled
checkbox_email.config(style='EmailEnabled.TCheckbutton')
ttk.Label(section_email, text="(Toggle to enable/disable email notifications)", foreground='gray', font=('Segoe UI', 8)).pack(side='left', padx=(10, 0))

# --- Control buttons section ---
section_controls = ttk.Frame(frame)
section_controls.pack(pady=(0, 15))

btn_start = ttk.Button(section_controls, text="▶️ Start App", command=start_app, width=15)
btn_start.pack(side='left', padx=5)

btn_stop = ttk.Button(section_controls, text="🛑 Stop App", command=stop_app, state="disabled", width=15)
btn_stop.pack(side='left', padx=5)

# --- Log area section ---
section_logs = ttk.LabelFrame(frame, text="Activity Logs", padding=10)
section_logs.pack(expand=True, fill='both')

log_box = tk.Text(section_logs, height=12, wrap='word', state='disabled', bg="#fafafa", font=('Consolas', 9), relief='flat')
log_box.pack(expand=True, fill='both')

# Add scrollbar for log
scrollbar = ttk.Scrollbar(section_logs, orient='vertical', command=log_box.yview)
scrollbar.pack(side='right', fill='y')
log_box.config(yscrollcommand=scrollbar.set)

# Configure text tags for coloring
log_box.tag_config("normal", foreground="black")
log_box.tag_config("error", foreground="red")
log_box.tag_config("timestamp", foreground="gray")

root.mainloop()