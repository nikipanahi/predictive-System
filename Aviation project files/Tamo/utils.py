import fitz  # این همان PyMuPDF است
import io
import requests
import base64

HF_API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/naver-clova-ix/donut-base-finetuned-docvqa"

def process_pdf_with_ai(pdf_path):
    try:
        # ۱. باز کردن PDF با PyMuPDF (بدون نیاز به Poppler)
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # لود کردن صفحه اول
        pix = page.get_pixmap()  # تبدیل صفحه به پیکسل (عکس)
        
        # ۲. تبدیل پیکسل‌ها به بایت‌های عکس (JPEG)
        img_bytes = pix.tobytes("jpg")

        # ۳. ارسال به Hugging Face
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        
        # پیشنهاد: ارسال مستقیم بایت‌ها (حجم کمتر و سرعت بیشتر)
        response = requests.post(API_URL, headers=headers, data=img_bytes)
        
        # اگر مدل در حال لود شدن باشد (خطای ۵۰۳)، اینجا مشخص می‌شود
        return response.json()

    except Exception as e:
        return {"error": str(e)}

def parse_ai_response(ai_text):
    # همان منطق قبلی برای استخراج متن
    import re
    serial_pattern = r"(?:serial|s/n|sn)[:\s]*([\w-]+)"
    serial = re.search(serial_pattern, ai_text, re.IGNORECASE)
    return serial.group(1) if serial else None