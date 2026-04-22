# apps/books/models.py
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name='عنوان')
    author = models.CharField(max_length=255, verbose_name='نویسنده')
    isbn = models.CharField(
        max_length=13,
        unique=True,
        verbose_name='شابک'
    )
    publisher = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='ناشر'
    )
    publish_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='سال انتشار'
    )
    category = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='دسته‌بندی'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='توضیحات'
    )

    total_copies = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد کل نسخه‌ها'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'کتاب'
        verbose_name_plural = 'کتاب‌ها'
        db_table = 'books'

    def __str__(self):
        return f"{self.title} — {self.author}"

    @property
    def available_copies(self):
        return self.copies.filter(status='available').count()


class BookCopy(models.Model):

    STATUS_CHOICES = [
        ('available', 'موجود'),
        ('borrowed', 'امانت داده شده'),
        ('damaged', 'آسیب‌دیده'),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='copies',
        verbose_name='کتاب'
    )
    copy_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد نسخه'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='وضعیت'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نسخه کتاب'
        verbose_name_plural = 'نسخه‌های کتاب'
        db_table = 'book_copies'

    def __str__(self):
        return f"{self.copy_code} — {self.book.title}"
