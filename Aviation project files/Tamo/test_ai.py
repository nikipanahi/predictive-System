import requests

# توکن خودت را اینجا جایگزین کن
API_TOKEN = "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" 
# یک مدل معروف برای درک تصاویر اسناد
API_URL = "https://api-inference.huggingface.co/models/microsoft/layoutlm-base-uncased"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def test_model():
    # یک متن ساده برای تست لود شدن مدل
    payload = {"inputs": "What is the serial number?"}
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ اتصال برقرار شد!")
        print("خروجی مدل:", response.json())
    elif response.status_code == 503:
        print("⏳ مدل در حال لود شدن است (Cold Start)... چند ثانیه صبر کنید و دوباره اجرا کنید.")
    else:
        print(f"❌ خطا با کد {response.status_code}:", response.text)

if __name__ == "__main__":
    test_model()