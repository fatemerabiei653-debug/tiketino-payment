from flask import Flask, request, render_template_string, session
import time
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tiketino_super_secret_key_2025_change_it_to_something_random'

# صفحه پرداخت با رمز پویا داخلی + پر شدن خودکار فیلد
PAYMENT_FORM = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>درگاه پرداخت Tiketino</title>
    <style>
        body {
            font-family: Tahoma, Arial, sans-serif;
            background: linear-gradient(to bottom, #e0f7fa, #a7ffeb);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 500px;
            margin: 30px auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: #0d47a1;
            color: white;
            padding: 25px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 10px 0 0; font-size: 18px; }
        .logo { width: 140px; margin: 20px auto; display: block; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .body { padding: 30px; }
        label { display: block; margin: 18px 0 8px; font-weight: bold; color: #333; }
        input, select { width: 100%; padding: 14px; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .row { display: flex; gap: 15px; }
        .row > div { flex: 1; }
        .otp-section { margin: 20px 0; padding: 15px; background: #f0f8ff; border-radius: 8px; border: 1px solid #bee5eb; text-align: center; }
        #timer { font-size: 18px; color: #d32f2f; font-weight: bold; margin: 10px 0; }
        .otp-code { font-size: 28px; color: #155724; background: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0; letter-spacing: 5px; font-family: monospace; }
        .btn { width: 100%; padding: 16px; background: #1976d2; color: white; border: none; border-radius: 8px; font-size: 18px; cursor: pointer; margin-top: 30px; }
        .btn:hover { background: #1565c0; }
        .btn-otp { background: #43a047; padding: 12px; font-size: 16px; }
        .btn-otp:hover { background: #388e3c; }
        .btn-otp:disabled { background: #aaa; cursor: not-allowed; }
        .secure { text-align: center; color: #666; font-size: 13px; margin-top: 25px; }
    </style>
    <script>
        function formatCard(input) {
            let value = input.value.replace(/\\D/g, '');
            value = value.substring(0, 16);
            let formatted = value.match(/.{1,4}/g);
            input.value = formatted ? formatted.join('-') : value;
        }

        let timeLeft = 0;
        let timerInterval;
        let generatedOtp = null;

        function generateOtp() {
            generatedOtp = Math.floor(100000 + Math.random() * 900000);
            document.getElementById('otp-code-display').innerText = generatedOtp;
            document.getElementById('otp-code-display').style.display = 'block';
            document.getElementById('otp-btn').disabled = true;

            timeLeft = 60;
            document.getElementById('timer').innerText = '01:00';

            timerInterval = setInterval(() => {
                timeLeft--;
                let m = '00';
                let s = String(timeLeft).padStart(2, '0');
                document.getElementById('timer').innerText = m + ':' + s;

                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    document.getElementById('timer').innerText = 'مهلت تمام شد';
                    document.getElementById('password').value = generatedOtp;  // پر شدن خودکار فیلد
                    document.getElementById('otp-btn').disabled = false;
                }
            }, 1000);
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>درگاه پرداخت نرم‌افزار Tiketino</h1>
            <p>پرداخت امن بلیط اتوبوس</p>
        </div>
        
        <img src="https://images.unsplash.com/photo-1558981806-ec527fa84c21?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" alt="اتوبوس Tiketino" class="logo">

        <div class="body">
            <form method="POST" action="/process">
                <input type="hidden" name="raw_amount" value="{{ raw_amount }}">
                <input type="hidden" name="order_id" value="{{ order_id }}">

                <label>شماره کارت</label>
                <input type="text" name="card_number" maxlength="19" placeholder="1234-5678-9012-3456" oninput="formatCard(this)" required>

                <div class="row">
                    <div><label>ماه انقضا</label><select name="expiry_month" required>
                        <option value="">ماه</option>
                        {% for m in range(1,13) %}
                        <option value="{{ '%02d' % m }}">{{ '%02d' % m }}</option>
                        {% endfor %}
                    </select></div>
                    <div><label>سال انقضا</label><select name="expiry_year" required>
                        <option value="">سال</option>
                        {% for y in range(1404, 1415) %}
                        <option value="{{ y }}">{{ y }}</option>
                        {% endfor %}
                    </select></div>
                    <div><label>CVV2</label><input type="text" name="cvv" maxlength="4" placeholder="123" required></div>
                </div>

                <div class="otp-section">
                    <button type="button" id="otp-btn" class="btn btn-otp" onclick="generateOtp()">دریافت رمز پویا</button>
                    <div id="otp-code-display" class="otp-code" style="display:none;"></div>
                    <div id="timer">ابتدا دکمه را فشار دهید</div>
                    <p style="color:#666; margin-top:15px;">پس از ۶۰ ثانیه، کد به طور خودکار در فیلد زیر وارد می‌شود</p>
                </div>

                <label>رمز دوم یا پویا (تست ثابت: 123456)</label>
                <input type="text" name="password" id="password" placeholder="رمز دوم یا کد پویا" maxlength="6" required>

                <button type="submit" class="btn">پرداخت</button>
            </form>

            <div class="secure">
                این درگاه دارای گواهینامه امنیت SSL و اتصال به شتاب است
            </div>
        </div>
    </div>
</body>
</html>
'''

# صفحه رسید پرداخت
RECEIPT_PAGE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رسید پرداخت - Tiketino</title>
    <style>
        body {
            font-family: Tahoma, Arial, sans-serif;
            background: linear-gradient(to bottom, #e0f7fa, #a7ffeb);
            padding: 30px;
            min-height: 100vh;
        }
        .receipt {
            max-width: 550px;
            margin: 40px auto;
            background: rgba(255,255,255,0.96);
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: #2e7d32;
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 26px; }
        .body { padding: 35px; line-height: 2.2; font-size: 17px; }
        .row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px dotted #aaa; }
        .label { font-weight: bold; color: #333; }
        .value { color: #555; text-align: left; direction: ltr; }
        .footer { text-align: center; padding: 25px; background: #e8f5e8; }
        .btn { display: inline-block; padding: 14px 40px; background: #1976d2; color: white; text-decoration: none; border-radius: 8px; font-size: 18px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <h1>✓ پرداخت با موفقیت انجام شد</h1>
            <p style="margin:10px 0 0; font-size:18px;">نرم‌افزار Tiketino</p>
        </div>
        <div class="body">
            <div class="row"><span class="label">مبلغ پرداختی:</span><span class="value">{{ amount }} تومان</span></div>
            <div class="row"><span class="label">شماره پیگیری:</span><span class="value">{{ ref_id }}</span></div>
            <div class="row"><span class="label">شماره سفارش:</span><span class="value">{{ order_id }}</span></div>
            <div class="row"><span class="label">پذیرنده:</span><span class="value">شرکت حمل و نقل اتوبوسرانی Tiketino</span></div>
            <div class="row"><span class="label">تاریخ پرداخت:</span><span class="value">{{ date }}</span></div>
            <div class="row"><span class="label">ساعت پرداخت:</span><span class="value">{{ time }}</span></div>
        </div>
        <div class="footer">
            <p style="font-size:18px; color:#2e7d32;">از اعتماد شما سپاسگزاریم</p>
            <p>بلیط شما به زودی در اپلیکیشن Tiketino قابل مشاهده است</p>
            <a href="/" class="btn">بازگشت</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@app.route('/pay/<int:amount>')
def pay(amount=50000):
    order_id = request.args.get('order_id', 'TKT' + str(random.randint(10000, 99999)))
    session.clear()
    return render_template_string(PAYMENT_FORM,
                                 amount=f"{amount:,}".replace(",", "٬"),
                                 raw_amount=amount,
                                 order_id=order_id)

@app.route('/process', methods=['POST'])
def process():
    time.sleep(3)  # تأخیر شبیه‌سازی درگاه

    raw_amount = int(request.form['raw_amount'])
    user_password = request.form['password']

    # قبول رمز ثابت 123456
    if user_password == "123456":
        valid = True
    else:
        valid = False

    if not valid:
        return "<h2 style='text-align:center;color:red;padding:100px;background:white;margin:50px;border-radius:12px;'>رمز اشتباه است!</h2><a href='/'>تلاش مجدد</a>"

    ref_id = random.randint(100000000000, 999999999999)
    now = datetime.now()
    date_persian = now.strftime("%Y/%m/%d")
    time_str = now.strftime("%H:%M:%S")
    formatted_amount = f"{raw_amount:,}".replace(",", "٬")

    return render_template_string(RECEIPT_PAGE,
                                 amount=formatted_amount,
                                 ref_id=ref_id,
                                 order_id=request.form['order_id'],
                                 date=date_persian,
                                 time=time_str)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
