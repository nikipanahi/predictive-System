import json
import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.feature_extraction.text import TfidfVectorizer

print("🤖 Running Re-engineered Predictive Maintenance Model...")

try:
    json_path = 'data.json'
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"فایل {json_path} پیدا نشد!")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        live_data = json.load(f)
        
    # ۱. استخراج دیتای اصلی
    df = pd.DataFrame(live_data['data'])
    
    # تمیزکاری اولیه ستون‌ها
    df['part_info'] = df['part_info'].fillna("unknown part").astype(str)
    df['actions_done'] = df['actions_done'].fillna("check").astype(str)
    
    # ۲. متغیر ورودی (X): تبدیل مشخصات و نام قطعه به عدد
    tfidf = TfidfVectorizer(max_features=15, stop_words='english')
    X_text = tfidf.fit_transform(df['part_info']).toarray()
    feature_names = tfidf.get_feature_names_out()
    
    X = pd.DataFrame(X_text, columns=feature_names)
    
    # ۳. متغیر خروجی (y): دستور تعمیری که صادر شده است
    y = df['actions_done']
    
    unique_actions = y.unique().tolist()
    print(f"🎯 دستورات تعمیری کشف شده در دیتا: {len(unique_actions)} مورد منفرد.")

    # ۴. آموزش مدل درخت تصمیم
    tree_model = DecisionTreeClassifier(max_depth=5, min_samples_split=4, random_state=42)
    tree_model.fit(X, y)

    # ۵. رسم درخت تصمیم با بارگذاری کاملاً مستقل کتابخانه گرافیکی
    import matplotlib.pyplot as safe_plt
    
    # ایجاد بوم نقاشی به صورت کاملاً ایزوله
    fig, ax = safe_plt.subplots(figsize=(25, 12), dpi=300)
    
    # ساختن نام‌های کوتاه برای کلاس‌ها (مثل Action 1, Action 2) برای جلوگیری از ارور متن‌های طولانی دیتا
    clean_class_names = [f"Action {i+1}" for i in range(len(unique_actions))]
    
    # رسم خود درخت روی بوم ایزوله شده
    plot_tree(
        tree_model, 
        filled=True, 
        feature_names=X.columns.tolist(),
        class_names=clean_class_names, 
        impurity=False, 
        rounded=True, 
        fontsize=6,
        ax=ax
    )
    
    ax.set_title('Aviation Maintenance Recommendation Strategy (Based on Part Specifications)', fontsize=14, fontweight='bold', pad=20)
    
    # ذخیره مستقیم فایل از روی آبجکت fig
    output_img = 'automated_aviation_tree.png'
    fig.savefig(output_img, dpi=300, bbox_inches='tight')
    safe_plt.close(fig)
    
    print("\n" + "="*50)
    print(f"✅ SUCCESS! The real recommendation tree saved as '{output_img}'.")
    print("="*50 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")