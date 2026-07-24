from django import forms
from .models import PartIn, PartMaster

class Tamo20Form(forms.ModelForm):
    DECISION_CHOICES_satisfied = forms.BooleanField(required=False)
    final_decision_satisfied = forms.BooleanField(required=False) 
    DECISION_CHOICES = [
        ('Accept', 'Accept'),
        ('Reject', 'Reject'),
    ]
    category_filter = forms.ChoiceField(
        choices=[('', '--- Select Category ---')] + PartMaster.CATEGORY_CHOICES,
        label="Select Part Type First",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_category_filter'})
    )

    final_decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Final Decision"
    )

    class Meta:
        model = PartIn
        fields = [
            'category_filter',
            'part_info',
            'work_order_no',
            'serial_number',
            'tracking_no',
            'customer',
            'qty',
            'status',
            'inspection_date',
            'final_decision',
            'inspected_by_name'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['work_order_no'].required = False
        widgets = {
            'part_info': forms.Select(attrs={'class': 'form-control'}),
            'work_order_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'W/O No.'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tracking_no': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'final_decision': forms.Select(attrs={'class': 'form-control'}),
            'inspected_by_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(Tamo20Form, self).__init__(*args, **kwargs)
        for i in range(1, 8):
            field_name = f'item_{i}_satisfied'
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})
