import os
import sys
import json

print("⏳ Connecting to offline database and exporting fields...")

# تنظیم خودکار مسیر برای لود شدن کامپوننت‌های پروژه
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings') # نام پوشه اصلی تنظیمات را جایگزین کن

try:
    import django
    django.setup()
    from app.models import Offline_Portal # نام مدل واقعی خودت را بگذار
    
    records = YourMaintenanceModel.objects.all()
    data_list = []
    
    for record in records:
        data_list.append({
            "part_info": record.part_info_id,
            "reason_of_removal": record.reason_of_removal, # استخراج متن گزارش واقعی تکنسین
            "action": record.status # اقدام یا وضعیت ثبت شده
        })
        
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Successfully updated data.json with {len(data_list)} real records!")

except Exception as e:
    print(f"❌ Connection Error: {e}")