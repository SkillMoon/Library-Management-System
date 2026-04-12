from django import forms
from .models import BorrowRequest, Borrow
from apps.books.models import BookCopy
from django.contrib.auth import get_user_model


class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['book', 'note']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class BorrowRequestResponseForm(forms.Form):
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

class BorrowIssueForm(forms.Form):
    book_copy = forms.ModelChoiceField(
        queryset=BookCopy.objects.none(),
        label="نسخه فیزیکی",
        empty_label="انتخاب کنید..."
    )

    def __init__(self, book, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book_copy'].queryset = BookCopy.objects.filter(
            book=book, status='available'
        )

class ReturnForm(forms.Form):
    CONDITION_CHOICES = [
        ('available', 'سالم'),
        ('damaged', 'آسیب‌دیده'),
    ]
    condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        label="وضعیت کتاب هنگام بازگشت"
    )

User = get_user_model()


class DirectBorrowForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['student', 'professor']).order_by('last_name'),
        label='کاربر (دانشجو / استاد)',
        empty_label='--- انتخاب کنید ---',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    book_copy = forms.ModelChoiceField(
        queryset=BookCopy.objects.filter(status='available').select_related('book'),
        label='نسخه کتاب (موجود)',
        empty_label='--- انتخاب کنید ---',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
