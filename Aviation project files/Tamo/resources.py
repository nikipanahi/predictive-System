from import_export import resources
from .models import PartIn  # نام درست مدل شما این است

class PartInResource(resources.ModelResource):
    class Meta:
        model = PartIn
        # تمام فیلدهایی که می‌خواهید در خروجی اکسل بیایند را اینجا لیست کنید
        fields = ('id', 'work_order_no', 'serial_number', 'customer', 'status', 'final_decision')