# apps/books/forms.py

from django import forms
from .models import Book, BookCopy


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'publisher',
            'publish_year', 'category', 'description', 'total_copies'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'publish_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'total_copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }

    def clean_total_copies(self):
        total = self.cleaned_data.get('total_copies')
        # ✅ مشکل ۳ برطرف شد
        if total is None or total < 1:
            raise forms.ValidationError('تعداد نسخه‌ها باید حداقل ۱ باشد.')
        return total

    def clean_publish_year(self):
        year = self.cleaned_data.get('publish_year')
        if year and (year < 1000 or year > 1500):
            raise forms.ValidationError('سال انتشار معتبر نیست (۱۰۰۰ تا ۱۵۰۰ شمسی).')
        return year


class BookCopyForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        # ✅ مشکل ۱ برطرف شد — فیلد book حذف شد
        fields = ['copy_code', 'status']
        widgets = {
            'copy_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: BC-001'
            }),
            # ✅ مشکل ۲ برطرف شد — choices از مدل خونده می‌شه
            'status': forms.Select(
                choices=BookCopy.STATUS_CHOICES,
                attrs={'class': 'form-control'}
            ),
        }

    def clean_copy_code(self):
        code = self.cleaned_data.get('copy_code', '').strip().upper()
        if not code:
            raise forms.ValidationError('کد نسخه نمی‌تواند خالی باشد.')
        qs = BookCopy.objects.filter(copy_code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('این کد نسخه قبلاً ثبت شده است.')
        return code
