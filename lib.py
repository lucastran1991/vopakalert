from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import subprocess
import os
import glob

def get_epoch_range(days_ahead=5):
    current_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = current_day + timedelta(days=days_ahead)
    
    start_epoch = int((current_day - timedelta(days=1)).timestamp() * 1000)  # epoch time dạng milliseconds
    end_epoch = int(end_day.timestamp() * 1000)
    
    return start_epoch, end_epoch

# --- Hàm gửi email ---
def send_email_alert(alert_type):
    if alert_type == "recommendation":
        subject = "[Critical Alert] Vopak Boiler Activity - Multiple Failures"
        body = "The system has detected multiple consecutive failures (5+) with Boiler Activity data. The service has been experiencing issues and requires immediate attention.\n\nPlease check the system."
    elif alert_type == "opcdie":
        subject = "[Critical Alert] OPC Data Issue - Multiple Failures"
        body = "The OPC data has been unavailable for multiple consecutive checks (5+). The service has been experiencing issues and requires immediate attention.\n\nPlease check the system."
    else:
        subject = "[Critical Alert] Website Down - Multiple Failures"
        body = "The monitored website has been down for multiple consecutive checks (5+). The service has been experiencing issues and requires immediate attention.\n\nPlease check the system."

    sender_email = "luanxinhdata@gmail.com"
    receiver_emails = [
        "lutran@atomiton.com",
        "ktran@atomiton.com",
        "ltran@atomiton.com"
    ]
    password = "xryl xwzy gdnq benp"  # App Password

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())

    print(f"✅ Alert email sent to: {', '.join(receiver_emails)}")

def check_recommendation(isNotify=True):
    # --- Tính epoch time ---
    start_epoch, end_epoch = get_epoch_range(5)

    print("Start epoch:", start_epoch)
    print("End epoch:", end_epoch)

    url = "http://vopakext.atomiton.com:8090/fid-vopaksteamact"

    payload = f"#\r\nGetBoilerActivityDetails({start_epoch},{end_epoch},5,0)"
    headers = {
        'UserToken': 'SuperUser',
        'Content-Type': 'text/plain'
    }

    print("payload:", payload)
    response = requests.post(url, headers=headers, data=payload)

    try:
        data = response.json()  # chuyển response sang JSON
        total_records = data.get("Message", {}).get("Value", {}).get("totalRecords", 0)

        if total_records < 5:
            print("Error: totalRecords < 5")
            result = f"❌ Failed: Only {total_records} records found (minimum 5 required)"
            if isNotify:
                send_email_alert("recommendation")
            return result
        else:
            print("OK, totalRecords =", total_records)
            return f"✅ Success: {total_records} records found"

    except json.JSONDecodeError:
        error_msg = "❌ Failed: Invalid JSON response"
        print("Error: Invalid JSON response")
        print("Raw response:", response.text)
        return error_msg

def check_production_status(isNotify=True):
    url = "http://bwcext.atomiton.com:8090/fid-tqlengineres/vopakui/index.html#/auth/login"
    try:
        response = requests.get(url, timeout=10)  # timeout 10 giây
        if response.status_code == 200:
            print("✅ Website is UP (status 200)")
            return "✅ Success: Website is UP (status 200)"
        else:
            result = f"❌ Failed: Website returned status {response.status_code}"
            print(result)
            if isNotify:
                send_email_alert("webdie")
            return result
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Failed: Website unreachable - {str(e)}"
        print("❌ Error: Website unreachable — web die")
        print("Detail:", e)
        if isNotify:
            send_email_alert("webdie")
        return error_msg

def check_OPC_data(isNotify=True):
    url = "http://vopakext.atomiton.com:8080/fid-DigitalTerminalInterface"
    payload = """<Query><Find limit="10" offset="0" orderBy="Notification.time desc"><Notification><alertText ne=""/></Notification></Find></Query>"""
    headers = {
        'userToken': 'SuperUser',
        'Content-Type': 'application/xml'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # raise lỗi nếu HTTP != 200
    except Exception as e:
        print(f"API request failed: {e}")
        return

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        print("Invalid XML response from server")
        return

    today = datetime.now(timezone.utc).date()
    today_notifications = []

    for result in root.findall('.//Result/Notification'):
        time_str = result.findtext('time')
        alert_text = result.findtext('alertText')

        if not time_str:
            continue

        try:
            notif_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            continue

        if notif_time.date() == today:
            today_notifications.append(alert_text)

    if not today_notifications:
        error_msg = "❌ Failed: No OPC notifications found today"
        print("error need to recheck the OPC")
        if isNotify:
            send_email_alert("opcdie")
        return error_msg
    else:
        result_msg = f"✅ Success: Found {len(today_notifications)} OPC notification(s) today"
        print("✅ OPC Notifications Today:")
        for alert in today_notifications:
            print(f"- {alert}")
        return result_msg

def restart_vopaksteam():
    """Restart Vopaksteam engine using Windows command"""
    command = 'tql -engine -start Path=F:\\atomitonsoftware\\vopaksteam'
    
    try:
        # Execute command on Windows
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            success_msg = "✅ Success: Vopaksteam engine restarted"
            print(success_msg)
            if result.stdout:
                print(f"Output: {result.stdout}")
            return success_msg
        else:
            error_msg = f"❌ Failed: Command returned code {result.returncode}"
            print(error_msg)
            if result.stderr:
                print(f"Error: {result.stderr}")
            return error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "❌ Failed: Command execution timed out"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Failed: {str(e)}"
        print(f"Error executing command: {e}")
        return error_msg

def initialize_system_value():
    """Initialize system value by sending HTTP POST with payloads from payload folder"""
    url = "http://localhost:8080/fid-DigitalTerminalInterface"
    payload_dir = "payload"
    
    # Find all XML files in payload directory
    try:
        if not os.path.exists(payload_dir):
            error_msg = f"❌ Failed: Payload directory '{payload_dir}' not found"
            print(error_msg)
            return error_msg
        
        # Get all XML files from payload directory
        payload_files = glob.glob(os.path.join(payload_dir, "*.xml"))
        payload_files.sort()  # Sort for consistent ordering
        
        if not payload_files:
            error_msg = f"❌ Failed: No XML files found in '{payload_dir}' directory"
            print(error_msg)
            return error_msg
        
        print(f"Found {len(payload_files)} payload file(s) to process")
        
    except Exception as e:
        error_msg = f"❌ Failed: Error accessing payload directory - {str(e)}"
        print(error_msg)
        return error_msg
    
    headers = {
        'userToken': 'SuperUser',
        'Content-Type': 'application/xml'
    }
    
    results = []
    success_count = 0
    failure_count = 0
    
    # Process each payload file
    for payload_file in payload_files:
        filename = os.path.basename(payload_file)
        
        # Read payload from file
        try:
            with open(payload_file, 'r', encoding='utf-8') as f:
                payload = f.read()
            
            if not payload.strip():
                print(f"⚠️ Warning: Payload file '{filename}' is empty, skipping")
                failure_count += 1
                results.append(f"{filename}: Empty file")
                continue
                
        except Exception as e:
            error_msg = f"Error reading '{filename}': {str(e)}"
            print(f"❌ {error_msg}")
            failure_count += 1
            results.append(f"{filename}: Read error")
            continue
        
        # Send HTTP POST request
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            
            success_msg = f"✅ {filename}: Success (status {response.status_code})"
            print(success_msg)
            success_count += 1
            results.append(f"{filename}: Success")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ {filename}: HTTP request failed - {str(e)}"
            print(error_msg)
            failure_count += 1
            results.append(f"{filename}: Request failed")
        except Exception as e:
            error_msg = f"❌ {filename}: Unexpected error - {str(e)}"
            print(f"Error: {error_msg}")
            failure_count += 1
            results.append(f"{filename}: Error")
    
    # Return summary
    if success_count == len(payload_files):
        summary = f"✅ Success: All {success_count} payload(s) initialized successfully"
    elif success_count > 0:
        summary = f"⚠️ Partial: {success_count} succeeded, {failure_count} failed out of {len(payload_files)} total"
    else:
        summary = f"❌ Failed: All {failure_count} payload(s) failed to initialize"
    
    print(f"\nSummary: {summary}")
    return summary