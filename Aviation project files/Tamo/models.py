import qrcode
import os
import uuid
from io import BytesIO
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# توابع کمکی برای مسیر فایل‌ها
def get_pdf_filename(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('parts_pdf/', f"{instance.part_info.part_number}_{instance.serial_number}.{ext}")

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('parts_pdfs/', filename)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self): return self.name

class PartMaster(models.Model):
    CATEGORY_CHOICES = [('Official', 'Official'), ('non-Official', 'non-Official')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parts')
    part_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Official')
    def __str__(self): return f"{self.part_number} - {self.category}"

class PartIn(models.Model):
    STATUS_CHOICES = [
        ('not started', 'Not Started'), ('in progress', 'In Progress'),
        ('rejected', 'Rejected'), ('waiting', 'Waiting'),
        ('completed', 'Completed'), ('delivered', 'Delivered'),
    ]
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='my_assigned_parts')
    part_info = models.ForeignKey(PartMaster, on_delete=models.CASCADE, related_name='entries')
    work_order_no = models.CharField(max_length=100, db_index=True)
    serial_number = models.CharField(max_length=100, db_index=True)
    tracking_no = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    customer = models.CharField(max_length=200, null=True, blank=True)
    qty = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not started')
    qr_code = models.ImageField(upload_to='part_qrcodes/', blank=True, null=True)
    is_delivered = models.BooleanField(default=False)
    delivery_date = models.DateField(null=True, blank=True)
    is_warranty_claim = models.BooleanField(default=False, verbose_name="Is Warranty?")
    updated_at = models.DateTimeField(auto_now=True)
    reason_of_removal = models.TextField(null=True, blank=True)
    is_audit_approved = models.BooleanField(default=False, verbose_name="approved")
    pdf_file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    repair_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    rejection_reason = models.TextField(null=True, blank=True)
    rejection_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # ۱. مدیریت زمان تکمیل تعمیر
        if self.status == 'completed' and not self.repair_completed_at:
            self.repair_completed_at = timezone.now()
        
        # ۲. مدیریت تاریخ تحویل
        if self.is_delivered and not self.delivery_date:
            self.delivery_date = timezone.now().date()

        # ۳. بهینه‌سازی QR Code (جلوگیری از تولید مجدد)
        if not self.qr_code:
            old_record = PartIn.objects.filter(
                part_info=self.part_info, 
                serial_number=self.serial_number
            ).exclude(pk=self.pk).only('qr_code').first()
            
            if old_record and old_record.qr_code:
                self.qr_code = old_record.qr_code

        super().save(*args, **kwargs)

    @property
    def net_repair_time(self):
        if self.repair_completed_at:
            delta = self.repair_completed_at - self.created_at
            return delta.days
        return None

    @property
    def time_in_service(self):
        if self.rejection_date and self.updated_at:
            delta = self.rejection_date - self.updated_at
            return abs(delta.days)
        return None

class PartInLog(models.Model):
    part_in = models.ForeignKey(PartIn, on_delete=models.CASCADE, related_name='logs')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class StatusHistory(models.Model):
    part_in = models.ForeignKey(PartIn, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)