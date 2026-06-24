import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.feature_extraction.text import TfidfVectorizer

print("🤖 Running Specialized Text-Mining Model on data.json...")

try:
    json_path = 'data.json'
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"فایل {json_path} پیدا نشد!")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        live_data = json.load(f)
        
    # استخراج بخش دیتای اصلی از ساختار جیسون شما
    df = pd.DataFrame(live_data['data'])
    
    # ۱. تنظیم دقیق ستون متنی (لاگ‌ها) و ستون وضعیت قطعه
    text_col = 'actions_done'
    df[text_col] = df[text_col].fillna("no record").astype(str)
    
    print(f"🔍 Selected Text Column for Analysis: '{text_col}'")
    
    # ۲. تبدیل متن به ویژگی‌های عددی واقعی (Text Mining) بر اساس کلمات کلیدی هوانوردی
    # کلمات کلیدی مهم مثل repaired, adjusted, checked در این بخش استخراج می‌شوند
    tfidf = TfidfVectorizer(max_features=10, stop_words='english')
    X_text = tfidf.fit_transform(df[text_col]).toarray()
    feature_names = tfidf.get_feature_names_out()
    
    print("\n" + "="*50)
    print(f"🎯 کلمات کلیدی واقعی کشف شده از متن لاگ‌ها:")
    print(list(feature_names))
    print("="*50 + "\n")

    # ۳. آماده‌سازی ورودی‌های مدل (X) و خروجی هدف (y)
    # در اینجا مدل یاد می‌گیرد بر اساس کلمات کلیدی لاگ‌ها، نوع قطعه را دسته‌بندی کند
    X = pd.DataFrame(X_text, columns=feature_names)
    
    # تفکیک بر اساس رسمی (Official) یا غیررسمی (non-Official) بودن قطعه
    y = df['part_info'].apply(lambda x: 1 if "Official" in str(x) and "non-Official" not in str(x) else 0)

    # ۴. آموزش مدل درخت تصمیم با عمق مناسب برای یک پلات شکیل علمی
    tree_model = DecisionTreeClassifier(max_depth=4, min_samples_split=4, random_state=42)
    tree_model.fit(X, y)

    # ۵. رسم درخت تصمیم مهندسی و فوق‌العاده تمیز برای مقاله شما
    plt.figure(figsize=(16, 8), dpi=300)
    plot_tree(
        tree_model, 
        filled=True, 
        feature_names=X.columns.tolist(),
        class_names=["Non-Official Part", "Official Part"],
        impurity=False, 
        rounded=True, 
        fontsize=9
    )
    
    plt.title('Shop-Floor Predictive Maintenance Strategy (Aviation Logs Text-Mining)', fontsize=14, fontweight='bold', pad=20)
    
    output_img = 'automated_aviation_tree.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Success! A beautiful multi-branch tree saved as '{output_img}'.")

except Exception as e:
    print(f"❌ Error: {e}")