from import_export import resources
from .models import PartIn 
class PartInResource(resources.ModelResource):
    class Meta:
        model = PartIn
        fields = ('id', 'work_order_no', 'serial_number', 'customer', 'status', 'final_decision')
