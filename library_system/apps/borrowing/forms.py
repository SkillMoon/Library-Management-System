from django import forms
from .models import BorrowRequest

class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['book', 'note']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class BorrowRequestResponseForm(forms.Form):
    """فرم پاسخ کتابدار به درخواست"""
    ACTION_CHOICES = [
        ('approved', 'تأیید'),
        ('rejected', 'رد'),
    ]
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='یادداشت'
    )
