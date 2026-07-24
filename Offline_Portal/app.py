from flask import Flask, render_template, send_from_directory
import json
import os

app = Flask(__name__)

# مسیر پوشه فایل‌های پیوست
ATTACHMENT_FOLDER = 'attachments'

@app.route('/')
def home():
    # خواندن دیتای سینک شده از فایل JSON
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            orders = json.load(f)
    else:
        orders = [] # اگر هنوز سینک نشده باشد
    
    return render_template('index.html', orders=orders)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(ATTACHMENT_FOLDER, filename)

if __name__ == '__main__':
    # اجرا روی پورت 8080
    print("Offline Portal is running on http://127.0.0.1:8080")
    app.run(debug=True, port=8080)