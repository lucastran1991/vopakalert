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
import time
import sys

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
    # List of commands to execute sequentially
    commands = [
        ("stop", "F:\\TQLEngine"),
        ("stop", "F:\\atomitonsoftware\\vopaksteam"),
        ("stop", "C:\\Edge\\TQLEngine"),
        ("start", "F:\\TQLEngine"),
        ("start", "F:\\atomitonsoftware\\vopaksteam"),
        ("start", "C:\\Edge\\TQLEngine"),
    ]
    
    results = []
    failed_commands = []
    
    try:
        # Execute each command sequentially
        for action, path in commands:
            command = f'tql -engine -{action} Path={path}'
            print(f"Executing: {command}")
            
            # Start commands may take longer, use 30 seconds timeout
            # Stop commands are usually faster, use 15 seconds
            timeout_seconds = 30 if action == "start" else 15
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds
                )
                
                if result.returncode == 0:
                    print(f"✅ {action.capitalize()} {path}: Success")
                    if result.stdout:
                        print(f"   Output: {result.stdout.strip()}")
                else:
                    error_info = f"{action.capitalize()} {path} failed (code {result.returncode})"
                    print(f"❌ {error_info}")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                    failed_commands.append(error_info)
                
                results.append((action, path, result.returncode == 0))
                
                # Wait 2 seconds between commands
                if action != commands[-1][0] or path != commands[-1][1]:  # Don't wait after last command
                    time.sleep(2)
                    
            except subprocess.TimeoutExpired:
                error_info = f"{action.capitalize()} {path} timed out"
                print(f"❌ {error_info}")
                failed_commands.append(error_info)
                results.append((action, path, False))
            except Exception as e:
                error_info = f"{action.capitalize()} {path} error: {str(e)}"
                print(f"❌ {error_info}")
                failed_commands.append(error_info)
                results.append((action, path, False))
        
        # Determine overall result
        success_count = sum(1 for _, _, success in results if success)
        total_count = len(results)
        
        if success_count == total_count:
            success_msg = f"✅ Success: All {total_count} engine command(s) executed successfully"
            print(success_msg)
            return success_msg
        elif success_count > 0:
            partial_msg = f"⚠️ Partial: {success_count}/{total_count} command(s) succeeded"
            if failed_commands:
                partial_msg += f" - Failed: {', '.join(failed_commands)}"
            print(partial_msg)
            return partial_msg
        else:
            error_msg = f"❌ Failed: All {total_count} command(s) failed"
            if failed_commands:
                error_msg += f" - {', '.join(failed_commands)}"
            print(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"❌ Failed: Unexpected error - {str(e)}"
        print(f"Error: {error_msg}")
        return error_msg

def initialize_system_value():
    """Initialize system value by sending HTTP POST with payloads from payload folder"""
    # Get the correct path for payload directory
    # When running as PyInstaller executable, use sys._MEIPASS
    # Otherwise, use current directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    payload_dir = os.path.join(base_path, "payload")
    
    # Also try relative path from current working directory (for development)
    if not os.path.exists(payload_dir):
        payload_dir = "payload"
    
    # Check if payload directory exists
    try:
        if not os.path.exists(payload_dir):
            error_msg = f"❌ Failed: Payload directory '{payload_dir}' not found"
            print(error_msg)
            print(f"   Searched in: {os.path.abspath(payload_dir)}")
            print(f"   Current working directory: {os.getcwd()}")
            return error_msg
    except Exception as e:
        error_msg = f"❌ Failed: Error accessing payload directory - {str(e)}"
        print(error_msg)
        return error_msg
    
    # Phase 1: Process XML files (init_payload_1.xml, init_payload_2.xml, init_payload_3.xml)
    url_xml = "http://localhost:8080/fid-DigitalTerminalInterface"
    headers_xml = {
        'userToken': 'SuperUser',
        'Content-Type': 'application/xml'
    }
    
    # Get XML files (specifically the first 3 payload files)
    xml_files = []
    for i in range(1, 4):
        xml_file = os.path.join(payload_dir, f"init_payload_{i}.xml")
        if os.path.exists(xml_file):
            xml_files.append(xml_file)
    
    if not xml_files:
        error_msg = f"❌ Failed: No XML payload files (init_payload_1.xml, init_payload_2.xml, init_payload_3.xml) found"
        print(error_msg)
        return error_msg
    
    print(f"Phase 1: Processing {len(xml_files)} XML payload file(s)...")
    
    xml_results = []
    xml_success_count = 0
    xml_failure_count = 0
    
    # Process each XML payload file
    for payload_file in xml_files:
        filename = os.path.basename(payload_file)
        
        # Read payload from file
        try:
            with open(payload_file, 'r', encoding='utf-8') as f:
                payload = f.read()
            
            if not payload.strip():
                print(f"⚠️ Warning: Payload file '{filename}' is empty, skipping")
                xml_failure_count += 1
                xml_results.append(f"{filename}: Empty file")
                continue
                
        except Exception as e:
            error_msg = f"Error reading '{filename}': {str(e)}"
            print(f"❌ {error_msg}")
            xml_failure_count += 1
            xml_results.append(f"{filename}: Read error")
            continue
        
        # Send HTTP POST request
        try:
            response = requests.post(url_xml, headers=headers_xml, data=payload, timeout=10)
            response.raise_for_status()
            
            success_msg = f"✅ {filename}: Success (status {response.status_code})"
            print(success_msg)
            xml_success_count += 1
            xml_results.append(f"{filename}: Success")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ {filename}: HTTP request failed - {str(e)}"
            print(error_msg)
            xml_failure_count += 1
            xml_results.append(f"{filename}: Request failed")
        except Exception as e:
            error_msg = f"❌ {filename}: Unexpected error - {str(e)}"
            print(f"Error: {error_msg}")
            xml_failure_count += 1
            xml_results.append(f"{filename}: Error")
    
    # Phase 2: Process energy optimization payload (init_payload_4.txt) only if all XML payloads succeeded
    energy_opt_success = False
    energy_opt_result = None
    
    if xml_success_count == len(xml_files):
        print(f"\nPhase 2: All {len(xml_files)} XML payload(s) succeeded. Processing Energy Optimization...")
        
        energy_opt_file = os.path.join(payload_dir, "init_payload_4.txt")
        url_energy_opt = "http://vopakext.atomiton.com:8090/fid-vopaksteam"
        headers_energy_opt = {
            'UserToken': 'SuperUser',
            'Content-Type': 'text/plain'
        }
        
        if os.path.exists(energy_opt_file):
            try:
                # Read energy optimization payload
                with open(energy_opt_file, 'r', encoding='utf-8') as f:
                    energy_opt_payload = f.read()
                
                if not energy_opt_payload.strip():
                    print("⚠️ Warning: Energy optimization payload file is empty")
                    energy_opt_result = "Init Energy Optimization: Empty file"
                else:
                    # Send HTTP POST request for energy optimization
                    response = requests.post(url_energy_opt, headers=headers_energy_opt, data=energy_opt_payload, timeout=10)
                    response.raise_for_status()
                    
                    success_msg = f"✅ Init Energy Optimization: Success (status {response.status_code})"
                    print(success_msg)
                    energy_opt_success = True
                    energy_opt_result = "Init Energy Optimization: Success"
                    
            except FileNotFoundError:
                error_msg = "❌ Init Energy Optimization: File not found"
                print(error_msg)
                energy_opt_result = "Init Energy Optimization: File not found"
            except requests.exceptions.RequestException as e:
                error_msg = f"❌ Init Energy Optimization: HTTP request failed - {str(e)}"
                print(error_msg)
                energy_opt_result = f"Init Energy Optimization: Request failed - {str(e)}"
            except Exception as e:
                error_msg = f"❌ Init Energy Optimization: Unexpected error - {str(e)}"
                print(f"Error: {error_msg}")
                energy_opt_result = f"Init Energy Optimization: Error - {str(e)}"
        else:
            print("⚠️ Warning: Energy optimization payload file (init_payload_4.txt) not found, skipping")
            energy_opt_result = "Init Energy Optimization: File not found"
    else:
        print(f"\n⚠️ Phase 2 skipped: {xml_failure_count} of {len(xml_files)} XML payload(s) failed. Energy optimization will not be executed.")
        energy_opt_result = "Init Energy Optimization: Skipped (XML payloads failed)"
    
    # Build summary
    total_operations = len(xml_files) + (1 if energy_opt_result else 0)
    total_success = xml_success_count + (1 if energy_opt_success else 0)
    
    if xml_success_count == len(xml_files) and energy_opt_success:
        summary = f"✅ Success: All {total_operations} operation(s) completed successfully ({len(xml_files)} XML payloads + Energy Optimization)"
    elif xml_success_count == len(xml_files) and energy_opt_result and not energy_opt_success:
        summary = f"⚠️ Partial: All {len(xml_files)} XML payload(s) succeeded, but Energy Optimization failed"
    elif xml_success_count > 0:
        summary = f"⚠️ Partial: {xml_success_count}/{len(xml_files)} XML payload(s) succeeded, Energy Optimization skipped"
    else:
        summary = f"❌ Failed: All {len(xml_files)} XML payload(s) failed, Energy Optimization skipped"
    
    print(f"\nSummary: {summary}")
    return summary