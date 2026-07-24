import json
import os
import re
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.feature_extraction.text import TfidfVectorizer

print("🤖 Running Precise P/N Predictive Maintenance Model...")

try:
    json_path = 'data.json'
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"فایل {json_path} پیدا نشد!")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        live_data = json.load(f)
        
    df = pd.DataFrame(live_data['data'])
    
    # تبدیل به حروف کوچک برای یکدست شدن
    df['part_info'] = df['part_info'].fillna("unknown").astype(str).str.lower()
    df['actions_done'] = df['actions_done'].fillna("check").astype(str).str.lower()
    
    # 🎯 دیکشنری مترجم هوشمند با پارت‌نامبرهای کامل هوانوردی
    # 🎯 دیکشنری مترجم هوشمند با نام‌های استاندارد و واقعی هوانوردی
    def translate_exact_aviation_parts(text):
        # پیدا کردن پارت‌نامبر کامل فلپ ایندیکیتور با پسوندهای احتمالی‌اش
        if '2061' in text:
            return 'flap_position_indicator'
        elif '4019700' in text:
            return 'electric_motor'
        elif '391046' in text or '391041' in text:
            return 'diode_rectifier'
        elif '07202' in text:
            return 'vhf_receiver'
        elif '473597' in text:
            return 'control_board'
        elif '0083' in text:
            return 'actuator_valve'
            
        # برای سایر قطعاتی که هنوز دستی نام‌گذاری نکرده‌ای
        extended_numbers = re.findall(r'\b\d+(?:-\d+)*\b', text)
        if extended_numbers and len(extended_numbers[0]) >= 3:
            safe_name = extended_numbers[0].replace('-', '_')
            return f"part_{safe_name}"
            
        return 'general_avionics_part'

    df['translated_part'] = df['part_info'].apply(translate_exact_aviation_parts)
    
    # دسته‌بندی اقدامات فنی
    def categorize_action(text):
        if 'repair' in text or 'fix' in text or 'resolder' in text or 'repaired' in text:
            return 'Repair'
        elif 'adjust' in text or 'calibrate' in text or 'realign' in text or 'adjusted' in text:
            return 'Adjustment'
        elif 'replace' in text or 'change' in text or 'cannibalize' in text or 'replaced' in text:
            return 'Replacement'
        return 'Ignore'

    df['clean_action'] = df['actions_done'].apply(categorize_action)
    df_filtered = df[df['clean_action'] != 'Ignore'].copy()

    print(f"📊 تعداد کل ردیف‌های فنی در حال پردازش: {len(df_filtered)}")

    # 🎯 تنظیم الگوی توکن در TF-IDF تا کلمات شامل آندرسکور (مثل flap_position_indicator) را کامل بردارد
    tfidf = TfidfVectorizer(max_features=30, token_pattern=r'(?u)\b[a-zA-Z0-9_]{3,}\b')
    X_text = tfidf.fit_transform(df_filtered['translated_part']).toarray()
    feature_names = tfidf.get_feature_names_out()
    X = pd.DataFrame(X_text, columns=feature_names)
    
    y = df_filtered['clean_action']
    unique_actions = sorted(y.unique().tolist())

    # آموزش مدل درخت تصمیم
    tree_model = DecisionTreeClassifier(max_depth=5, min_samples_split=2, random_state=42)
    tree_model.fit(X, y)

    # خروجی پلات استاندارد DOT
    output_dot_file = "aviation_tree_exact.dot"
    export_graphviz(
        tree_model,
        out_file=output_dot_file,
        feature_names=X.columns.tolist(),
        class_names=unique_actions,
        filled=True,
        rounded=True,
        special_characters=True,
        impurity=False
    )
    
    print("\n" + "="*50)
    print(f"✅ SUCCESS! Exact part-number tree saved as '{output_dot_file}'.")
    print("="*50 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")