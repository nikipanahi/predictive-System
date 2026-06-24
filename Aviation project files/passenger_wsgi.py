import os
import sys

# ۱. پیدا کردن مسیر دقیق پوشه ساب‌دامین شما
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# ۲. تزریق اجباری و دستی هر دو مسیر پکیج‌ها (معمولی و ۶۴ بیتی) به پایتون سرور
VENV_LIB = "/home/aryatamo/virtualenv/dashboard.aryatamo.com/3.12/lib/python3.12/site-packages"
VENV_LIB64 = "/home/aryatamo/virtualenv/dashboard.aryatamo.com/3.12/lib64/python3.12/site-packages"

if VENV_LIB64 not in sys.path:
    sys.path.insert(1, VENV_LIB64)
if VENV_LIB not in sys.path:
    sys.path.insert(2, VENV_LIB)

# ۳. معرفی پوشه تنظیمات اصلی به جنگو
os.environ['DJANGO_SETTINGS_MODULE'] = 'inventory_site.settings'

# ۴. فراخوانی و ران کردن لودر رسمی جنگو
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # اگر باز هم مشکلی بود، ارور دقیق را روی صفحه مرورگر به ما نشان بدهد
    def application(environ, start_response):
        start_response('500 Internal Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [f"<h1>🚨 Django Startup Error</h1><p style='color:red;'><b>Details:</b> {str(e)}</p>".encode('utf-8')]
SILENCED_SYSTEM_CHECKES=['fields.E210']