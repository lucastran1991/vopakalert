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


def log_message(msg):
    """Ghi log ra Text box"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_box.config(state='normal')
    log_box.insert(tk.END, f"[{timestamp}] {msg}\n")
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
                lambda: safe_run(check_recommendation, "Check Recommendation")
            )
            log_message(f"✅ Scheduled: check_recommendation() every {interval_rec} minutes")

        if var_production.get():
            interval_prod = int(entry_production.get())
            if interval_prod <= 0:
                raise ValueError
            schedule.every(interval_prod).minutes.do(
                lambda: safe_run(check_production_status, "Check Production Status")
            )
            log_message(f"✅ Scheduled: check_production_status() every {interval_prod} minutes")

        if var_opc.get():
            interval_opc = int(entry_opc.get())
            if interval_opc <= 0:
                raise ValueError
            schedule.every(interval_opc).minutes.do(
                lambda: safe_run(check_OPC_data, "Check OPC Data")
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

    log_message("▶️ Scheduler started.")
    threading.Thread(target=run_scheduler, daemon=True).start()


def safe_run(func, name):
    """Chạy hàm an toàn, có log"""
    try:
        log_message(f"Running: {name}() ...")
        func()
        log_message(f"✅ Finished: {name}()")
    except Exception as e:
        log_message(f"❌ Error in {name}(): {e}")


def stop_app():
    """Dừng toàn bộ task"""
    global running
    running = False
    schedule.clear()
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")
    log_message("🛑 Stopping all scheduled tasks...")


# ------------------ UI ------------------
root = tk.Tk()
root.title("Vopak Monitor")
root.geometry("600x400")

frame = ttk.Frame(root, padding=15)
frame.pack(expand=True, fill='both')

# --- Task selection ---
ttk.Label(frame, text="Select tasks and frequency (minutes):", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=5)

# Task 1
var_recommend = tk.BooleanVar()
frame_rec = ttk.Frame(frame)
frame_rec.pack(anchor='w', pady=5, fill='x')
ttk.Checkbutton(frame_rec, text="Check Recommendation", variable=var_recommend).pack(side='left')
ttk.Label(frame_rec, text="Every").pack(side='left', padx=(10, 0))
entry_recommend = ttk.Entry(frame_rec, width=6)
entry_recommend.insert(0, "5")
entry_recommend.pack(side='left')
ttk.Label(frame_rec, text="min").pack(side='left', padx=(2, 0))

# Task 2
var_production = tk.BooleanVar()
frame_prod = ttk.Frame(frame)
frame_prod.pack(anchor='w', pady=5, fill='x')
ttk.Checkbutton(frame_prod, text="Check Production Status", variable=var_production).pack(side='left')
ttk.Label(frame_prod, text="Every").pack(side='left', padx=(10, 0))
entry_production = ttk.Entry(frame_prod, width=6)
entry_production.insert(0, "10")
entry_production.pack(side='left')
ttk.Label(frame_prod, text="min").pack(side='left', padx=(2, 0))

# Task 3
var_opc = tk.BooleanVar()
frame_opc = ttk.Frame(frame)
frame_opc.pack(anchor='w', pady=5, fill='x')
ttk.Checkbutton(frame_opc, text="Check OPC Data", variable=var_opc).pack(side='left')
ttk.Label(frame_opc, text="Every").pack(side='left', padx=(10, 0))
entry_opc = ttk.Entry(frame_opc, width=6)
entry_opc.insert(0, "3")  # mặc định mỗi 3 phút
entry_opc.pack(side='left')
ttk.Label(frame_opc, text="min").pack(side='left', padx=(2, 0))

# --- Buttons ---
frame_btn = ttk.Frame(frame)
frame_btn.pack(pady=10)
btn_start = ttk.Button(frame_btn, text="▶️ Start App", command=start_app)
btn_start.pack(side='left', padx=10)
btn_stop = ttk.Button(frame_btn, text="🛑 Stop App", command=stop_app, state="disabled")
btn_stop.pack(side='left', padx=10)

# --- Log area ---
ttk.Label(frame, text="Logs:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 0))
log_box = tk.Text(frame, height=10, wrap='word', state='disabled', bg="#f4f4f4")
log_box.pack(expand=True, fill='both')

root.mainloop()