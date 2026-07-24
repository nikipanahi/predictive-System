import fitz 
import io
import requests
import base64
import os
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "YOUR_HUGGINGFACE_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/naver-clova-ix/donut-base-finetuned-docvqa"
def process_pdf_with_ai(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0) 
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("jpg")
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        response = requests.post(API_URL, headers=headers, data=img_bytes)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
def parse_ai_response(ai_text):
    import re
    serial_pattern = r"(?:serial|s/n|sn)[:\s]*([\w-]+)"
    serial = re.search(serial_pattern, ai_text, re.IGNORECASE)
    return serial.group(1) if serial else None
