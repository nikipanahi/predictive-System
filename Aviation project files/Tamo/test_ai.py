import requests
API_TOKEN = "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" 
API_URL = "https://api-inference.huggingface.co/models/microsoft/layoutlm-base-uncased"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def test_model():
    payload = {"inputs": "What is the serial number?"}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        print("✅ connected!")
        print("output:", response.json())
    elif response.status_code == 503:
        print("⏳ loading (Cold Start)... .")
    else:
        print(f"❌ error {response.status_code}:", response.text)

if __name__ == "__main__":
    test_model()
