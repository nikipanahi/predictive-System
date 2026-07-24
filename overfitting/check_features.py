import json
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    json_path = 'data.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        live_data = json.load(f)
        
    df = pd.DataFrame(live_data['data'])
    df['part_info'] = df['part_info'].fillna("unknown").astype(str)
    df['actions_done'] = df['actions_done'].fillna("check").astype(str).str.lower()
    
    # دقیقاً همان فیلتر و پیش‌پردازش کد اصلی شما
    def categorize_action(text):
        if 'repair' in text or 'fix' in text or 'resolder' in text or 'repaired' in text: return 'Repair Job'
        elif 'adjust' in text or 'calibrat' in text or 'realign' in text or 'adjusted' in text: return 'Adjustment Job'
        elif 'replace' in text or 'change' in text or 'cannibaliz' in text or 'replaced' in text: return 'Replacement Job'
        return 'Ignore'

    df['clean_action'] = df['actions_done'].apply(categorize_action)
    df_filtered = df[df['clean_action'] != 'Ignore'].copy()

    custom_stop_words = ['english', 'non', 'official', 'status', 'changed', 'part', 'info', 'unknown']
    tfidf = TfidfVectorizer(max_features=30, stop_words=custom_stop_words, token_pattern=r'(?u)\b[a-zA-Z0-9]{3,}\b')
    tfidf.fit(df_filtered['part_info'])
    
    # 🎯 استخراج لیست کلمات کلیدی واقعی به ترتیب قرارگیری در مدل
    feature_names = tfidf.get_feature_names_out()
    
    print("\n🔒 ================== SECURITY FEATURE DECODER ==================")
    print("این لیست فقط در ترمینال شما نمایش داده می‌شود و در فایل عکس ذخیره نشده است:\n")
    
    for index, name in enumerate(feature_names):
        print(f"🔹 Feature Column [{index}]: {name}")
        
    print("=================================================================\n")

except Exception as e:
    print(f"❌ Error: {e}")