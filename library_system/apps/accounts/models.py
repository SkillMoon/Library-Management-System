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

    @property
    def fine_rate(self):
        """نرخ جریمه روزانه بر اساس نقش"""
        if self.role == self.Role.PROFESSOR:
            return 2000
        return 5000  # student و بقیه
