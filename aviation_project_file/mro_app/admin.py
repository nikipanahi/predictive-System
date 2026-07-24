from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import DateWidget, ForeignKeyWidget
from .models import Customer, PartIn, PartMaster, PartInLog

# ۱. تنظیمات وارد کردن داده‌ها
class PartInResource(resources.ModelResource):
    part_info = fields.Field(
        column_name='part_info',
        attribute='part_info',
        widget=ForeignKeyWidget(PartMaster, 'part_number')
    )
    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateWidget(format='%d.%b.%Y')
    )
    inspection_date = fields.Field(
        column_name='inspection_date',
        attribute='inspection_date',
        widget=DateWidget(format='%d.%b.%Y')
    )

    class Meta:
        model = PartIn
        # فیلدها دقیقا مطابق ترتیب فایل اکسل/CSV شما
        fields = ('part_info', 'work_order_no', 'serial_number', 'customer', 'status', 'tracking_no', 'qty', 'inspection_date', 'created_at')
        import_id_fields = [] # اگر میخواهید ردیف تکراری آپدیت شود، اینجا 'work_order_no' را بگذارید
        force_init_instance = True

    def before_import_row(self, row, **kwargs):
        pn = row.get('part_info')
        if pn:
            PartMaster.objects.get_or_create(
                part_number=pn,
                defaults={
                    'user': User.objects.first(),
                    'description': 'Auto-created during import',
                    'category': 'Official'
                }
            )

# ۲. مدیریت لاگ‌ها (Inlines)
class PartInLogInline(admin.TabularInline):
    model = PartInLog
    extra = 1
    readonly_fields = ('author', 'created_at')
    fields = ('created_at', 'author', 'text')

# ۳. ثبت مدل‌ها
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(PartMaster)
class PartMasterAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'category', 'user')
    search_fields = ('part_number', 'description')

@admin.register(PartIn)
class PartInAdmin(ImportExportModelAdmin):
    resource_class = PartInResource
    inlines = [PartInLogInline]
    list_display = ('work_order_no', 'get_part_no', 'serial_number', 'status_colored', 'print_button')
    list_filter = ('status', 'customer')
    search_fields = ('work_order_no', 'serial_number', 'part_info__part_number')
    autocomplete_fields = ['part_info']

    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',)
        }

    def status_colored(self, obj):
        configs = {
            'completed': {'bg': '#d4edda', 'color': '#155724', 'icon': 'check-circle'},
            'in progress': {'bg': '#fff3cd', 'color': '#856404', 'icon': 'spinner'},
            'not started': {'bg': '#f8d7da', 'color': '#721c24', 'icon': 'clock'},
            'delivered': {'bg': '#d1ecf1', 'color': '#0c5460', 'icon': 'paper-plane'},
            'waiting': {'bg': '#e2e3e5', 'color': '#383d41', 'icon': 'pause-circle'},
            'deferred': {'bg': '#efd9ff', 'color': '#5a347b', 'icon': 'calendar-minus'},
        }
        conf = configs.get(obj.status, {'bg': '#eee', 'color': '#333', 'icon': 'info-circle'})
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; min-width: 80px; text-align: center;">'
            '<i class="fas fa-{}"></i> {}</span>',
            conf['bg'], conf['color'], conf['icon'], obj.get_status_display()
        )
    status_colored.short_description = 'Status'

    def print_button(self, obj):
        return format_html('<a class="button" style="color: white; background: #2c3e50; border-radius: 50px; padding: 4px 12px; font-size: 10px;" href="/part/{}/pdf/" target="_blank">PDF 🖨️</a>', obj.pk)
    print_button.short_description = 'Action'

    def get_part_no(self, obj):
        return obj.part_info.part_number if obj.part_info else "-"
    get_part_no.short_description = 'P/N'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_style'] = format_html("""
            <style>
                #result_list thead th {{ background: #447e9b !important; color: white !important; text-transform: uppercase; font-size: 11px; }}
                #result_list tbody tr:hover {{ background: #f0f7fa !important; }}
                .field-get_part_no {{ font-family: 'Courier New', monospace; font-weight: bold; color: #d63384; }}
            </style>
        """)
        return super().changelist_view(request, extra_context=extra_context)

    # اصلاح شده برای ذخیره حتمی لاگ‌ها
    def save_formset(self, request, form, formset, change):
        # ذخیره موقت داده‌های فرم‌ست
        instances = formset.save(commit=False)
        
        # مدیریت ردیف‌هایی که تیک حذف خورده‌اند
        for obj in formset.deleted_objects:
            obj.delete()

        # پردازش هر لاگ به صورت جداگانه
        for instance in instances:
            if isinstance(instance, PartInLog):
                # ۱. حتما نویسنده را به کاربر فعلی ست کن (بسیار مهم)
                instance.author = request.user
                
                # ۲. ست کردن قطعه مربوطه (اتصال لاگ به PartIn)
                # در برخی موارد ایمپورت شده، این اتصال خودکار انجام نمی‌شود
                if not hasattr(instance, 'part_in') or instance.part_in is None:
                    instance.part_in = form.instance
                
                # ۳. ذخیره نهایی هر آبجکت
                instance.save()
        
        # ۴. ذخیره روابط چند به چند (اگر وجود داشته باشد)
        formset.save_m2m()