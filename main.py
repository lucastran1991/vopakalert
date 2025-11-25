import requests
import json
from datetime import datetime, timedelta
from lib import get_epoch_range
from lib import send_email_alert
from lib import check_recommendation
from lib import check_production_status
from lib import check_OPC_data
from lib import restart_vopaksteam
from lib import initialize_system_value
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time


running = False  # Control flag for run/stop
email_enabled = False  # Email enable/disable flag

# Cooldown mechanism
failure_counts = {}  # Track failures per task type
last_failure_time = {}  # Track last failure time per task type
failure_threshold = 5  # Default: 5 failures before sending warning
cooldown_hours = 1  # Default: 1 hour cooldown after failure


def log_message(msg, is_error=False):
    """Write log to Text box with optional red color for errors"""
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


def get_next_rounded_time():
    """Calculate rounded up time to the next minute"""
    now = datetime.now()
    # Round up to next minute, set seconds and microseconds to 0
    next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    return next_minute


def schedule_repeated_task(task_func, task_name, interval_minutes, task_key):
    """Schedule task to run repeatedly at rounded time with cooldown mechanism"""
    def run_and_reschedule():
        if not running:
            return
        
        # Run the task with cooldown check
        result = run_with_cooldown(task_func, task_name, task_key)
        
        # Determine next run time based on result
        if running:
            if result and result.startswith("❌"):
                # Task failed - use cooldown period (1 hour)
                next_time = datetime.now() + timedelta(hours=cooldown_hours)
                log_message(f"⏸️ Cooldown active. Next check for {task_name} in {cooldown_hours} hour(s)")
            else:
                # Task succeeded - use normal interval
                next_time = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=interval_minutes)
            
            delay_seconds = (next_time - datetime.now()).total_seconds()
            if delay_seconds > 0 and running:
                threading.Timer(delay_seconds, run_and_reschedule).start()
    
    # Get next rounded minute
    next_minute = get_next_rounded_time()
    
    # Calculate delay to next rounded minute
    delay_seconds = (next_minute - datetime.now()).total_seconds()
    
    # Schedule first run at next rounded minute
    if delay_seconds > 0:
        threading.Timer(delay_seconds, run_and_reschedule).start()
    
    log_message(f"✅ Scheduled: {task_name} starting at {next_minute.strftime('%H:%M')}, then every {interval_minutes} minutes")


def run_with_cooldown(task_func, task_name, task_key):
    """Run task with cooldown mechanism"""
    global failure_counts, last_failure_time
    
    # Initialize counters if needed
    if task_key not in failure_counts:
        failure_counts[task_key] = 0
    if task_key not in last_failure_time:
        last_failure_time[task_key] = None
    
    # Run the task
    result = safe_run(task_func, task_name)
    
    # Check if it failed
    if result and result.startswith("❌"):
        # Task failed
        failure_counts[task_key] += 1
        last_failure_time[task_key] = datetime.now()
        
        # Check if we've exceeded threshold
        if failure_counts[task_key] >= failure_threshold:
            log_message(f"⚠️ {task_name} has failed {failure_counts[task_key]} times!", is_error=True)
            if email_enabled:
                try:
                    send_email_alert(get_alert_type_for_task(task_key))
                    log_message(f"📧 Warning email sent for {task_name}")
                except Exception as e:
                    log_message(f"❌ Failed to send warning email: {e}", is_error=True)
        else:
            log_message(f"📊 Failure count for {task_name}: {failure_counts[task_key]}/{failure_threshold}")
    else:
        # Task succeeded - reset counter
        if failure_counts[task_key] > 0:
            log_message(f"✅ {task_name} recovered. Failure counter reset.")
        failure_counts[task_key] = 0
        last_failure_time[task_key] = None
    
    return result


def get_alert_type_for_task(task_key):
    """Map task key to alert type"""
    mapping = {
        "recommend": "recommendation",
        "production": "webdie",
        "opc": "opcdie"
    }
    return mapping.get(task_key, "webdie")


def parse_time_string(time_str):
    """Parse HH:MM:SS time string and return (hour, minute, second)"""
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2])
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                return (hour, minute, second)
        raise ValueError("Invalid time format")
    except (ValueError, IndexError):
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM:SS")


def schedule_daily_action(task_func, task_name, time_str):
    """Schedule task to run daily at specific time"""
    # Parse time string first
    try:
        hour, minute, second = parse_time_string(time_str)
    except ValueError as e:
        log_message(f"❌ Invalid time format for {task_name}: {e}", is_error=True)
        return
    
    def run_and_reschedule():
        if not running:
            return
        
        # Run the task (no cooldown, just execute)
        result = safe_run(task_func, task_name)
        
        # Reschedule for next day
        if running:
            # Calculate next day at same time
            now = datetime.now()
            target_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
            
            # If time has passed today, schedule for tomorrow
            if target_time <= now:
                target_time += timedelta(days=1)
            
            delay_seconds = (target_time - datetime.now()).total_seconds()
            if delay_seconds > 0 and running:
                threading.Timer(delay_seconds, run_and_reschedule).start()
    
    # Calculate first run time
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
    
    # If time has passed today, schedule for tomorrow
    if target_time <= now:
        target_time += timedelta(days=1)
    
    delay_seconds = (target_time - datetime.now()).total_seconds()
    
    if delay_seconds > 0:
        threading.Timer(delay_seconds, run_and_reschedule).start()
        log_message(f"✅ Scheduled: {task_name} daily at {time_str}. Next run: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        log_message(f"❌ Failed to schedule {task_name}: invalid time calculation", is_error=True)


def start_app():
    """Start running tasks with rounded time"""
    global running, failure_threshold, cooldown_hours
    
    # Update settings from UI
    try:
        failure_threshold = int(entry_threshold.get())
        if failure_threshold <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive number for failure threshold.")
        return
    
    try:
        cooldown_hours = int(entry_cooldown.get())
        if cooldown_hours <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive number for cooldown hours.")
        return
    
    running = True

    # Get interval for each task
    try:
        if var_recommend.get():
            interval_rec = int(entry_recommend.get())
            if interval_rec <= 0:
                raise ValueError
            schedule_repeated_task(
                lambda: check_recommendation(isNotify=False),  # Email handled by cooldown
                "Check Recommendation",
                interval_rec,
                "recommend"
            )

        if var_production.get():
            interval_prod = int(entry_production.get())
            if interval_prod <= 0:
                raise ValueError
            schedule_repeated_task(
                lambda: check_production_status(isNotify=False),  # Email handled by cooldown
                "Check Production Status",
                interval_prod,
                "production"
            )

        if var_opc.get():
            interval_opc = int(entry_opc.get())
            if interval_opc <= 0:
                raise ValueError
            schedule_repeated_task(
                lambda: check_OPC_data(isNotify=False),  # Email handled by cooldown
                "Check OPC Data",
                interval_opc,
                "opc"
            )

    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive numbers for minutes.")
        return

    # Schedule daily actions
    try:
        if var_restart.get():
            time_str = entry_restart_time.get().strip()
            if not time_str:
                raise ValueError("Time cannot be empty")
            parse_time_string(time_str)  # Validate format
            schedule_daily_action(
                restart_vopaksteam,
                "Restart Vopaksteam",
                time_str
            )

        if var_init_system.get():
            time_str = entry_init_time.get().strip()
            if not time_str:
                raise ValueError("Time cannot be empty")
            parse_time_string(time_str)  # Validate format
            schedule_daily_action(
                initialize_system_value,
                "Initialize System Value",
                time_str
            )
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid time format: {e}\nPlease use HH:MM:SS format (e.g., 00:00:00)")
        return

    if not (var_recommend.get() or var_production.get() or var_opc.get() or var_restart.get() or var_init_system.get()):
        messagebox.showwarning("Warning", "Please select at least one task.")
        return

    # Update Start/Stop button
    btn_start.config(state="disabled")
    btn_stop.config(state="normal")
    
    # Disable all checkboxes while running
    checkbox_recommend.config(state="disabled")
    checkbox_production.config(state="disabled")
    checkbox_opc.config(state="disabled")
    checkbox_restart.config(state="disabled")
    checkbox_init_system.config(state="disabled")
    
    # Disable email checkbox
    checkbox_email.config(state="disabled")
    
    # Disable all entry fields
    entry_recommend.config(state="disabled")
    entry_production.config(state="disabled")
    entry_opc.config(state="disabled")
    entry_restart_time.config(state="disabled")
    entry_init_time.config(state="disabled")
    
    # Disable settings fields
    entry_threshold.config(state="disabled")
    entry_cooldown.config(state="disabled")

    next_time = get_next_rounded_time()
    log_message(f"▶️ Scheduler started. First run at {next_time.strftime('%H:%M:%S')}")


def safe_run(func, name):
    """Run function safely with logging and result capture"""
    try:
        log_message(f"Running: {name}() ...")
        result = func()
        if result:
            log_message(f"Result: {result}")
        log_message(f"✅ Finished: {name}()")
        return result
    except Exception as e:
        log_message(f"❌ Error in {name}(): {e}", is_error=True)
        return f"❌ Failed: {str(e)}"


def safe_send_email(alert_type):
    """Send email safely, only send if enabled"""
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
    """Stop all tasks"""
    global running, failure_counts, last_failure_time
    running = False
    # Reset failure counters
    failure_counts.clear()
    last_failure_time.clear()
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")
    
    # Enable all checkboxes after stopping
    checkbox_recommend.config(state="normal")
    checkbox_production.config(state="normal")
    checkbox_opc.config(state="normal")
    checkbox_restart.config(state="normal")
    checkbox_init_system.config(state="normal")
    
    # Enable email checkbox
    checkbox_email.config(state="normal")
    
    # Enable all entry fields
    entry_recommend.config(state="normal")
    entry_production.config(state="normal")
    entry_opc.config(state="normal")
    entry_restart_time.config(state="normal")
    entry_init_time.config(state="normal")
    
    # Enable settings fields
    entry_threshold.config(state="normal")
    entry_cooldown.config(state="normal")
    
    log_message("🛑 Stopping all scheduled tasks...")


def manual_restart_and_init():
    """Manually trigger restart engine and initialize system value"""
    def execute_actions():
        # Disable button while operation is in progress
        btn_manual_restart.config(state="disabled")
        
        try:
            log_message("🔄 Manual restart and initialize triggered...")
            
            # Step 1: Restart Vopaksteam
            log_message("Step 1: Restarting Vopaksteam engine...")
            restart_result = safe_run(restart_vopaksteam, "Restart Vopaksteam")
            
            # Delay 1 minute to wait for system to successfully start up
            time.sleep(60)
            
            # Step 2: Initialize System Value (regardless of restart result)
            log_message("Step 2: Initializing system value...")
            init_result = safe_run(initialize_system_value, "Initialize System Value")
            
            # Log completion
            if restart_result and restart_result.startswith("✅") and init_result and init_result.startswith("✅"):
                log_message("✅ Manual restart and initialize completed successfully")
            elif restart_result and restart_result.startswith("✅"):
                log_message("⚠️ Restart succeeded but initialization had issues", is_error=True)
            elif init_result and init_result.startswith("✅"):
                log_message("⚠️ Restart had issues but initialization succeeded", is_error=True)
            else:
                log_message("❌ Manual restart and initialize completed with errors", is_error=True)
                
        except Exception as e:
            log_message(f"❌ Error during manual restart and initialize: {e}", is_error=True)
        finally:
            # Re-enable button after completion
            btn_manual_restart.config(state="normal")
    
    # Run in background thread to avoid blocking UI
    threading.Thread(target=execute_actions, daemon=True).start()


# ------------------ UI ------------------
root = tk.Tk()
root.title("Vopak Monitor")
root.geometry("650x680")

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

# --- Scheduled Actions section ---
section_actions = ttk.LabelFrame(frame, text="Scheduled Actions", padding=15)
section_actions.pack(fill='x', pady=(0, 15))

ttk.Label(section_actions, text="Select actions and daily trigger time (HH:MM:SS):", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 10))

# Action 1 - Restart Vopaksteam
var_restart = tk.BooleanVar()
frame_restart = ttk.Frame(section_actions)
frame_restart.pack(anchor='w', pady=5, fill='x')
checkbox_restart = ttk.Checkbutton(frame_restart, text="Restart Vopaksteam", variable=var_restart, width=25)
checkbox_restart.pack(side='left')
ttk.Label(frame_restart, text="At").pack(side='left', padx=(10, 5))
entry_restart_time = ttk.Entry(frame_restart, width=10, justify='center')
entry_restart_time.insert(0, "00:00:00")
entry_restart_time.pack(side='left')
ttk.Label(frame_restart, text="daily", foreground='gray', font=('Segoe UI', 8)).pack(side='left', padx=(5, 0))

# Action 2 - Initialize System Value
var_init_system = tk.BooleanVar()
frame_init = ttk.Frame(section_actions)
frame_init.pack(anchor='w', pady=5, fill='x')
checkbox_init_system = ttk.Checkbutton(frame_init, text="Initialize System Value", variable=var_init_system, width=25)
checkbox_init_system.pack(side='left')
ttk.Label(frame_init, text="At").pack(side='left', padx=(10, 5))
entry_init_time = ttk.Entry(frame_init, width=10, justify='center')
entry_init_time.insert(0, "00:10:00")
entry_init_time.pack(side='left')
ttk.Label(frame_init, text="daily", foreground='gray', font=('Segoe UI', 8)).pack(side='left', padx=(5, 0))

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

# --- Settings section ---
section_settings = ttk.LabelFrame(frame, text="Cooldown Settings", padding=10)
section_settings.pack(fill='x', pady=(0, 10))

frame_threshold = ttk.Frame(section_settings)
frame_threshold.pack(anchor='w', pady=3)
ttk.Label(frame_threshold, text="Failure threshold").pack(side='left', padx=(0, 5))
entry_threshold = ttk.Entry(frame_threshold, width=6, justify='center')
entry_threshold.insert(0, "5")
entry_threshold.pack(side='left')
ttk.Label(frame_threshold, text="(Send warning after N failures)", foreground='gray', font=('Segoe UI', 8)).pack(side='left', padx=(5, 0))

frame_cooldown = ttk.Frame(section_settings)
frame_cooldown.pack(anchor='w', pady=3)
ttk.Label(frame_cooldown, text="Cooldown period").pack(side='left', padx=(0, 5))
entry_cooldown = ttk.Entry(frame_cooldown, width=6, justify='center')
entry_cooldown.insert(0, "1")
entry_cooldown.pack(side='left')
ttk.Label(frame_cooldown, text="hour(s) (Wait before retry after failure)", foreground='gray', font=('Segoe UI', 8)).pack(side='left', padx=(5, 0))

# --- Control buttons section ---
section_controls = ttk.Frame(frame)
section_controls.pack(pady=(0, 15))

btn_start = ttk.Button(section_controls, text="▶️ Start App", command=start_app, width=15)
btn_start.pack(side='left', padx=5)

btn_stop = ttk.Button(section_controls, text="🛑 Stop App", command=stop_app, state="disabled", width=15)
btn_stop.pack(side='left', padx=5)

# --- Manual action button section ---
section_manual = ttk.Frame(frame)
section_manual.pack(pady=(0, 15))

btn_manual_restart = ttk.Button(section_manual, text="🔄 Force Restart & Initialize", command=manual_restart_and_init, width=30)
btn_manual_restart.pack()

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