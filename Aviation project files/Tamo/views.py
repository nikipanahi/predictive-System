import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import PartIn, PartMaster, Customer, PartInLog, StatusHistory

from django.core.paginator import Paginator # حتما این را در بالای فایل اضافه کنید
# مدل‌ها
from .models import PartIn, PartMaster, Customer, PartInLog, StatusHistory
# کمکی‌های AI
from .utils import process_pdf_with_ai, parse_ai_response

# 1. صفحه اصلی و لیست
@login_required
def add_part(request):
    customers = Customer.objects.all().order_by('name')
    all_parts = PartMaster.objects.all()


    if request.method == "POST":
        pn_input = request.POST.get('part_number', '').strip()
        sn_input = request.POST.get('serial_number', '').strip()
        cust_id = request.POST.get('customer_id')
        reason = request.POST.get('reason_of_removal', '')
        is_non_off = request.POST.get('is_non_official') == 'true'
        pdf_file = request.FILES.get('pdf_file')

        master_item = PartMaster.objects.filter(part_number=pn_input).first()
        customer_obj = Customer.objects.get(id=cust_id)
        cust_code = f"{customer_obj.code}"
        date_code = timezone.now().strftime('%y%m')
        prefix_n = "N" if is_non_off else ""

        # --- منطق جلوگیری از WO تکراری ---
        count = 1
        while True:
            generated_wo = f"{date_code}-{cust_code}-{prefix_n}{count:02d}"
            if not PartIn.objects.filter(work_order_no=generated_wo).exists():
                break
            count += 1
        # --------------------------------

        try:
            PartIn.objects.create(
                part_info=master_item,
                work_order_no=generated_wo,
                serial_number=sn_input or "N/A",
                customer=customer_obj.name,
                reason_of_removal=reason, # اضافه شدن فیلد دلیل باز شدن
                pdf_file=pdf_file,
                created_at=timezone.now()
            )
            messages.success(request, f"Work Order {generated_wo} created.")
            return redirect('inventory_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'add_part.html', {'customers': customers, 'all_parts': all_parts, 'now': timezone.now()})
@login_required
def inventory_list(request):
    # ۱. گرفتن پارامترهای فیلتر از آدرس (URL)
    search_query = request.GET.get('search', '')
    customer_filter = request.GET.get('customer', '')
    show_archive = request.GET.get('show_archive', 'false') == 'true'

    # ۲. کوئری پایه (شامل تمام قطعات)
    all_parts = PartIn.objects.select_related('part_info').all().order_by('-created_at')

    # ۳. اعمال فیلتر جستجو (در پارت‌نامبر، سریال یا Work Order)
    if search_query:
        all_parts = all_parts.filter(
            Q(work_order_no__icontains=search_query) |
            Q(part_info__part_number__icontains=search_query) |
            Q(serial_number__icontains=search_query)
        )

    # ۴. اعمال فیلتر مشتری
    if customer_filter:
        all_parts = all_parts.filter(customer=customer_filter)

    # ۵. جدا کردن آرشیو از موارد جاری (بر اساس وضعیت delivered)
    if show_archive:
        parts_list = all_parts.filter(status='delivered')
    else:
        parts_list = all_parts.exclude(status='delivered')

    # ۶. منطق صفحه‌بندی (Paginator) - برای اینکه دکمه‌های Next/Prev کار کنند
    paginator = Paginator(parts_list, 20) # نمایش ۲۰ مورد در هر صفحه
    page_number = request.GET.get('page')
    parts_obj = paginator.get_page(page_number)

    # ۷. آماده‌سازی آمار کارت‌های بالای صفحه
    context = {
        'parts': parts_obj,  # این همان متغیری است که در HTML شما استفاده شده
        'all_parts_count': PartIn.objects.count(),
        'in_shop_count': PartIn.objects.exclude(status='delivered').count(),
        'delivered_count': PartIn.objects.filter(status='delivered').count(),
        'all_customers': Customer.objects.values_list('name', flat=True),
        'selected_customer': customer_filter,
        'search_query': search_query,
        'show_archive': show_archive,
    }

    return render(request, 'inventory.html', context)
# 3. حذف قطعه
@login_required
def delete_part(request, pk):
    part = get_object_or_404(PartIn, pk=pk)
    part.delete()
    return redirect('inventory_list')

# 4. تاریخچه
@login_required
def part_history(request, pk):
    # دریافت قطعه
    part = get_object_or_404(PartIn, pk=pk)
    
    # گرفتن تمام لاگ‌های فنی مربوط به این قطعه
    # مطمئن شو که در مدل PartInLog فیلد ForeignKey به PartIn نامش part_in است
    logs_list = PartInLog.objects.filter(part_in=part).order_by('-created_at')
    
    # گرفتن تاریخچه وضعیت
    status_list = StatusHistory.objects.filter(part_in=part).order_by('-changed_at')
    
    return render(request, 'part_history.html', {
        'part': part,
        'logs': logs_list,
        'status_history': status_list
    })

# 5. ویرایش
# 5. ویرایش (نسخه اصلاح شده برای ذخیره تاریخ و آماده‌سازی داده‌های ML)
@login_required
def edit_part(request, pk):
    part = get_object_or_404(PartIn, pk=pk)
    old_status = part.status # جایگزین هوشمند برای tracker
    all_users = User.objects.all()
    serial_history = PartIn.objects.filter(serial_number=part.serial_number).exclude(pk=part.pk).order_by('-created_at')

    if request.method == "POST":
        new_note = request.POST.get('note')
        status_input = request.POST.get('status')
        if status_input:
            part.status = status_input
        assigned_to_id = request.POST.get('assigned_to')
        reason = request.POST.get('reason_of_removal')
        
        # مدیریت گارانتی و ادمین
        part.is_warranty_claim = 'is_warranty_claim' in request.POST
        if request.user.is_staff:
            part.is_audit_approved = 'is_audit_approved' in request.POST

        # مدیریت تاریخ تحویل
        part.is_delivered = 'is_delivered' in request.POST
        delivery_date_input = request.POST.get('delivery_date')
        
        if delivery_date_input:
            part.delivery_date = delivery_date_input
        elif part.is_delivered and not part.delivery_date:
            part.delivery_date = timezone.now().date()
        
        # تعیین وضعیت
        if part.is_delivered:
            part.status = 'delivered'
        else:
            part.status = status_input

        # ثبت تاریخچه (بدون نیاز به tracker)
        if old_status != part.status:
            StatusHistory.objects.create(
                part_in=part,
                status=part.status,
                changed_by=request.user
            )

        # ثبت لاگ فنی
        if new_note and new_note.strip():
            PartInLog.objects.create(
                part_in=part,
                author=request.user,
                text=new_note
            )

        # آپدیت نهایی
        part.reason_of_removal = reason
        if assigned_to_id:
            try:
                part.assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                part.assigned_to = None
        
        part.save()
        messages.success(request, f"Work Order {part.work_order_no} updated.")
        return redirect('inventory_list')

    return render(request, 'edit_part.html', {
        'part': part,
        'serial_history': serial_history,
        'all_users': all_users
    })
# 6. خروجی PDF (Tamo20)
@login_required
def generate_tamo20_pdf(request, pk):
    # کدهای مربوط به ReportLab یا WeasyPrint برای تولید PDF
    return HttpResponse("PDF Generation for Tamo20")

# 7. داشبورد و آمار
@login_required
def admin_dashboard(request):
    return render(request, 'dashboard.html')

# 8. خروجی اکسل
@login_required
def export_inventory_excel(request):
    # کدهای مربوط به openpyxl یا pandas
    return HttpResponse("Excel Export Link")

# 9. اسکنر و QR
@login_required
def inventory_scanner(request):
    return render(request, 'scanner.html')

@login_required
def verify_qr_api(request, pk):
    return JsonResponse({'status': 'verified'})

# 10. گزارش بازرسی (Audit)
@login_required
def inventory_audit_report(request):
    # این خط را اضافه کنید تا فقط قطعات تایید شده (تیک سبز) را بکشد
    approved_parts = PartIn.objects.filter(is_audit_approved=True).order_by('-updated_at')
    
    # حتما باید داده‌ها را با نام 'parts' (یا هر نامی که در HTML استفاده کردید) به تمپلیت بفرستید
    return render(request, 'audit_report.html', {'parts': approved_parts})

# 11. رهگیری قطعه (Tracking)
def track_part_history(request, part_no, serial_no):
    return render(request, 'track.html')

# 12. تغییر وضعیت بازرسی (AJAX & Normal)
@login_required
def toggle_audit_status(request, pk):
    part = get_object_or_404(PartIn, pk=pk)
    part.is_audit_approved = not part.is_audit_approved
    part.save()
    return redirect('inventory_list')

@login_required
def toggle_audit_status_ajax(request, pk):
    part = get_object_or_404(PartIn, pk=pk)
    part.is_audit_approved = not part.is_audit_approved
    part.save()
    return JsonResponse({'new_status': part.is_audit_approved})

# 13. دریافت جزئیات قطعه (API)
@login_required
def get_part_details(request):
    pn = request.GET.get('part_no')
    part = PartMaster.objects.filter(part_number=pn).values().first()
    return JsonResponse(part, safe=False)
@login_required
def check_serial_history(request):
    pn = request.GET.get('part_number', '').strip()
    sn = request.GET.get('serial_number', '').strip()
    current_reason = request.GET.get('reason', '').strip() # دلیل خرابی فعلی را هم بگیریم
    
    estimated_lead_time = "Insufficient Data"
    warning_message = ""
    troubleshoot_hint = ""
    history_data = []

    if pn:
        # ۱. سیستم هشدار تعداد سوابق
        history_count = PartIn.objects.filter(part_info__part_number=pn, status='delivered').count()
        if 0 < history_count < 5:
            warning_message = f"Note: Only {history_count} records found. Prediction accuracy may be low."
        elif history_count == 0:
            warning_message = "First time this Part Number enters the system."

        # ۲. منطق پیشنهاد هوشمند (Troubleshooting Hint)
        if current_reason:
            from django.db.models import Count
            similar_cases = PartIn.objects.filter(
                part_info__part_number=pn,
                reason_of_removal__icontains=current_reason,
                action_taken__isnull=False
            ).values('action_taken').annotate(count=Count('action_taken')).order_by('-count')

            if similar_cases.exists():
                top_fix = similar_cases[0]
                total = sum(c['count'] for c in similar_cases)
                percentage = (top_fix['count'] / total) * 100
                
                if percentage >= 70: # اگر بالای ۷۰٪ بود، پیشنهاد را بساز
                    troubleshoot_hint = f"Smart Tip: In {int(percentage)}% of cases with '{current_reason}', the fix was: {top_fix['action_taken']}"

        # ۳. پیش‌بینی زمان (ML مدل)
        try:
            import joblib
            model = joblib.load('repair_estimator_model.pkl')
            encoders = joblib.load('label_encoders.pkl')
            pn_enc = encoders['part_info__part_number'].transform([pn])[0]
            current_month = timezone.now().month
            prediction = model.predict([[pn_enc, 0, 0, 0, current_month]])
            estimated_lead_time = f"{int(prediction[0])} Days"
        except:
            # Fallback به میانگین دیتابیس
            from django.db.models import Avg
            queryset = PartIn.objects.filter(part_info__part_number=pn, repair_completed_at__isnull=False)
            if queryset.exists():
                durations = [(q.repair_completed_at - q.created_at).days for q in queryset if q.repair_completed_at]
                if durations:
                    avg_days = sum(durations) / len(durations)
                    estimated_lead_time = f"{int(avg_days)} Days (Avg)"

    # ۴. تاریخچه سریال (جدول زرد)
    if pn and sn:
        past_entries = PartIn.objects.filter(part_info__part_number=pn, serial_number=sn).order_by('-created_at')
        for entry in past_entries:
            history_data.append({
                'wo': entry.work_order_no,
                'date': entry.created_at.strftime('%Y-%m-%d'),
                'customer': str(entry.customer),
                'status': entry.get_status_display(),
                'reason': entry.reason_of_removal or "N/A"
            })

    return JsonResponse({
        'exists': len(history_data) > 0,
        'estimated_lead_time': estimated_lead_time,
        'warning': warning_message,
        'hint': troubleshoot_hint, # فیلد جدید برای پیشنهاد هوشمند
        'history': history_data
    })
from django.db.models import Avg, F
from django.db.models import Avg, F, ExpressionWrapper, fields
from sklearn.linear_model import LinearRegression
@login_required
def mark_as_repaired(request, pk):
    part = get_object_or_404(PartIn, pk=pk)
    part.status = 'repaired' 
    part.repair_completed_at = timezone.now() 
    part.save()
    return redirect('inventory_list') # یا هر مسیری که لیست قطعات را نشان می‌دهد
@login_required
def report_failure(request, pk):
    old_part = get_object_or_404(PartIn, pk=pk)
    
    if request.method == 'POST':
        # ۱. تولید شماره WO جدید (مثلا با اضافه کردن پسوند R برای Rejected)
        # یا استفاده از همان منطق تولید WO که در add_part داشتی
        date_code = timezone.now().strftime('%y%m')
        cust_code = old_part.work_order_no.split('-')[1] # کد مشتری را از WO قبلی بردار
        
        count = 1
        while True:
            new_wo = f"{date_code}-{cust_code}-R{count:02d}" # R برای Re-entry
            if not PartIn.objects.filter(work_order_no=new_wo).exists():
                break
            count += 1

        # ۲. ایجاد یک رکورد کاملاً جدید (Clone)
        new_part = PartIn.objects.create(
            part_info=old_part.part_info,
            work_order_no=new_wo,
            serial_number=old_part.serial_number,
            customer=old_part.customer,
            reason_of_removal=request.POST.get('reason'),
            is_warranty_claim=True,
            status='not started', # قطعه جدید باید از اول شروع شود
            created_at=timezone.now()
        )

        # ۳. ثبت در لاگ فنی قطعه جدید که این قطعه مربوط به کدام WO قبلی بوده
        PartInLog.objects.create(
            part_in=new_part,
            author=request.user,
            text=f"Re-entry from previous WO: {old_part.work_order_no}. Reason: {request.POST.get('reason')}"
        )

        messages.success(request, f"New Work Order {new_wo} generated for this return.")
        return redirect('inventory_list')
    
    return redirect('inventory_list')
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib # برای ذخیره مدل
def train_advanced_model():
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    import joblib
    from Tamo.models import PartIn

    # ۱. استخراج داده‌های غنی‌تر از دیتابیس
    data = PartIn.objects.filter(repair_completed_at__isnull=False).values(
        'part_info__part_number', 
        'customer', 
        'reason_of_removal', 
        'assigned_to__username', # تعمیرکار
        'created_at', 
        'repair_completed_at'
    )
    
    if not data.exists():
        return "داده کافی برای آموزش مدل وجود ندارد!"

    df = pd.DataFrame(list(data))
    
    # ۲. پیش‌پردازش زمان و استخراج ماه
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['repair_completed_at'] = pd.to_datetime(df['repair_completed_at'])
    df['duration'] = (df['repair_completed_at'] - df['created_at']).dt.days
    df['month'] = df['created_at'].dt.month # استخراج ماه سال

    # ۳. تبدیل متون به عدد (Encoding) برای تمام ویژگی‌های جدید
    # از دیکشنری برای نگهداری انکودرها استفاده می‌کنیم تا بعداً در پیش‌بینی استفاده شوند
    encoders = {}
    categorical_features = ['part_info__part_number', 'customer', 'reason_of_removal', 'assigned_to__username']
    
    for col in categorical_features:
        le = LabelEncoder()
        # پر کردن مقادیر خالی برای جلوگیری از ارور
        df[col] = df[col].fillna('Unknown')
        df[f'{col}_enc'] = le.fit_transform(df[col])
        encoders[col] = le

    # ۴. تعریف ویژگی‌های ورودی (X) و هدف (y)
    features = [f'{col}_enc' for col in categorical_features] + ['month']
    X = df[features]
    y = df['duration']
    
    # ۵. آموزش مدل Random Forest
    model = RandomForestRegressor(n_estimators=200, random_state=42) # تعداد درخت‌ها را بیشتر کردیم
    model.fit(X, y)

    # ۶. تحلیل اهمیت ویژگی‌ها (Feature Importance)
    importances = model.feature_importances_
    influence_report = dict(zip(['Part Number', 'Customer', 'Reason', 'Technician', 'Month'], importances))
    
    print("\n--- تحلیل هوشمند تأثیر عوامل بر زمان تعمیر ---")
    for feature, score in influence_report.items():
        print(f"تأثیر {feature}: {score * 100:.2f}%")
        
    # ۷. ذخیره مدل و تمام انکودرها
    joblib.dump(model, 'repair_estimator_model.pkl')
    joblib.dump(encoders, 'label_encoders.pkl')
    
    return influence_report
from django.db import connection
def fix_db(request):
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE Tamo_partin ADD COLUMN rejection_reason TEXT;")
        cursor.execute("ALTER TABLE Tamo_partin ADD COLUMN rejection_date DATETIME;")
    return HttpResponse("Database patched!")
    
    
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
def get_cluster_based_hint(pn, current_reason):
    # ۱. واکشی تمام سوابق تعمیراتی این پارت نامبر که دارای Action Taken هستند
    past_records = PartIn.objects.filter(part_info__part_number=pn, action_taken__isnull=False).values('reason_of_removal', 'action_taken')
    
    if past_records.count() < 5: # اگر دیتا خیلی کم باشد، خوشه بندی معنا ندارد
        return None

    df = pd.DataFrame(list(past_records)) 
    # ۲. برداری کردن متن (TF-IDF)
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df['reason_of_removal'])

    # ۳. اجرای خوشه بندی (تعداد خوشه ها را به نسبت دیتا تنظیم کن)
    num_clusters = min(len(df) // 2, 5) # یک منطق ساده برای تعیین تعداد خوشه
    model = KMeans(n_clusters=num_clusters, random_state=42)
    df['cluster'] = model.fit_predict(X)

    # ۴. پیش‌بینی خوشه برای دلیل خرابی جدید
    new_vec = vectorizer.transform([current_reason])
    predicted_cluster = model.predict(new_vec)[0]

    # ۵. پیدا کردن بهترین راه حل در آن خوشه
    cluster_fixes = df[df['cluster'] == predicted_cluster]['action_taken'].value_counts()
    
    if not cluster_fixes.empty:
        top_fix = cluster_fixes.index[0]
        percentage = (cluster_fixes.iloc[0] / cluster_fixes.sum()) * 100
        return f"Based on semantic analysis, in {int(percentage)}% of similar cases, the solution was: {top_fix}"
    
    return None
from django.http import JsonResponse
from .models import PartIn

def export_for_offline(request):
    try:
        data = []
        # گرفتن تمام قطعات از دیتابیس
        parts = PartIn.objects.all()
        
        for part in parts:
            # ۱. حل مشکل کلید خارجی (PartMaster): 
            # اگر فیلد part_info پر بود، رشته متنی آن را می‌گیریم (مثلاً نام یا کد فنی قطعه)
            part_name = str(part.part_info) if part.part_info else "not detected"
            
            # ۲. پیدا کردن تمام کارهای انجام‌شده (لاگ‌ها) برای این قطعه
            logs = list(part.logs.values_list('text', flat=True))
            actions_done = "\n".join(logs) if logs else "no record"
            
            # ۳. ساختن ساختار جیسون تمیز
            part_data = {
                'work_order_no': getattr(part, 'work_order_no', 'not detected'),
                'part_info': part_name,  # حالا تبدیل به متن خوانا شد و دیگر ارور نمی‌دهد
                'pdf_file': part.pdf_file.url if part.pdf_file else None,
                'actions_done': actions_done
            }
            data.append(part_data)
            
        # خروجی جیسون خوانا و فارسی‌فرندلی
        return JsonResponse({'status': 'success', 'data': data}, safe=False, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        # اگر باز هم فیلد دیگری ناسازگار بود، خطا را اینجا چاپ می‌کند
        return JsonResponse({
            'status': 'error', 
            'message': f"خطا در استخراج اطلاعات دیتابیس: {str(e)}"
        }, status=500)