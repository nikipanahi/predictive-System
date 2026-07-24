import json
import os
import pandas as pd
from collections import Counter
import re

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        live_data = json.load(f)
        
    df = pd.DataFrame(live_data['data'])
    df['part_info'] = df['part_info'].fillna("unknown").astype(str).str.lower()
    
    # جمع‌آوری تمام کلمات و شماره‌های داخل ستون قطعات
    all_words = []
    custom_stop_words = ['english', 'non', 'official', 'status', 'changed', 'part', 'info', 'unknown']
    
    for text in df['part_info']:
        # استخراج کلمات و اعداد با طول حداقل ۳ کاراکتر
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text)
        for w in words:
            if w not in custom_stop_words:
                all_words.append(w)
                
    # شمارش تکرار هر کلمه
    word_counts = Counter(all_words)
    
    print("\n🔒 ====== لیست خود کلمات و پارت‌نامبرهای واقعی در دیتای شما ======")
    for word, count in word_counts.most_common(30):
        print(f"📄 کلمه/شماره واقعی: [{word}]  <--- تعداد تکرار در دیتا: {count} بار")
    print("===============================================================\n")

except Exception as e:
    print(f"❌ Error: {e}")