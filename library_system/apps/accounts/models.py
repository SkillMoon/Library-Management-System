from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'مدیر سیستم'
        LIBRARIAN = 'librarian', 'کتابدار'
        STUDENT = 'student', 'دانشجو'
        PROFESSOR = 'professor', 'استاد'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='نقش'
    )
    national_id = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name='کد ملی'
    )
    phone = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        verbose_name='شماره تماس'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class ImportLog(models.Model):
    imported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='import_logs',
        verbose_name='وارد کننده'
    )
    file_name = models.CharField(max_length=255, verbose_name='نام فایل')
    total_rows = models.IntegerField(verbose_name='کل ردیف‌ها')
    success_count = models.IntegerField(verbose_name='موفق')
    fail_count = models.IntegerField(verbose_name='ناموفق')
    errors = models.TextField(blank=True, verbose_name='خطاها')
    imported_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان import')

    class Meta:
        verbose_name = 'لاگ import'
        verbose_name_plural = 'لاگ‌های import'
        db_table = 'import_logs'

    def __str__(self):
        return f"{self.file_name} - {self.imported_at:%Y-%m-%d %H:%M}"
