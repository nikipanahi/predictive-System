import requests
import json
import os

# آدرس سرور محلی جنگو (روی سیستم خودت)
SERVER_URL = "http://127.0.0.1:8000/api/sync/" 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ATTACH_DIR = os.path.join(BASE_DIR, 'attachments')

# مطمئن می‌شویم پوشه attachments وجود دارد
if not os.path.exists(ATTACH_DIR):
    os.makedirs(ATTACH_DIR)

def run_sync():
    print("Connecting to main server...")
    try:
        # ۱. دریافت داده‌های متنی از جنگو
        response = requests.get(SERVER_URL, timeout=10)
        orders = response.json()
        
        # ۲. ذخیره در فایل JSON محلی برای استفاده مینی‌سایت
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=4, ensure_ascii=False)
        
        # ۳. دانلود فایل‌های PDF پیوست شده
        for order in orders:
            file_url = order.get('attachment')  # آدرس کامل فایل روی سرور
            if file_url:
                # اگر آدرس فایل نسبی بود (مثلا با media/ شروع می‌شد)، آن را کامل می‌کنیم
                if not file_url.startswith('http'):
                    file_url = f"http://127.0.0.1:8000{file_url}"
                
                file_name = file_url.split('/')[-1]
                save_path = os.path.join(ATTACH_DIR, file_name)
                
                # دانلود فایل فقط در صورتی که قبلاً دانلود نشده باشد
                if not os.path.exists(save_path):
                    print(f"Downloading: {file_name}")
                    file_res = requests.get(file_url, timeout=10)
                    with open(save_path, 'wb') as f:
                        f.write(file_res.content)
        
        print("✅ Synchronization successful!")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")

if __name__ == "__main__":
    run_sync()
    