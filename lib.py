from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def get_epoch_range(days_ahead=5):
    current_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = current_day + timedelta(days=days_ahead)
    
    start_epoch = int((current_day - timedelta(days=1)).timestamp() * 1000)  # epoch time dạng milliseconds
    end_epoch = int(end_day.timestamp() * 1000)
    
    return start_epoch, end_epoch

# --- Hàm gửi email ---
def send_email_alert(alert_type):
    if alert_type == "recommendation":
        subject = "[Alert] Vopak Boiler Activity"
        body = "System detected an issue with Boiler Activity data. Please check the system."
    elif alert_type == "opcdie":
        subject = "[Alert] OPC Data Issue"
        body = "The OPC data is not available. Please check the system."
    else:
        subject = "[Alert] Website Down"
        body = "The monitored website is down. Please check the system."

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
            if isNotify:
                send_email_alert("recommendation")
        else:
            print("OK, totalRecords =", total_records)

    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        print("Raw response:", response.text)

def check_production_status(isNotify=True):
    url = "http://bwcext.atomiton.com:8090/fid-tqlengineres/vopakui/index.html#/auth/login"
    try:
        response = requests.get(url, timeout=10)  # timeout 10 giây
        if response.status_code == 200:
            print("✅ Website is UP (status 200)")
        else:
            if isNotify:
                send_email_alert("webdie")
    except requests.exceptions.RequestException as e:
        print("❌ Error: Website unreachable — web die")
        print("Detail:", e)

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
        print("error need to recheck the OPC")
        if isNotify:
            send_email_alert("opcdie")
    else:
        print("✅ OPC Notifications Today:")
        for alert in today_notifications:
            print(f"- {alert}")