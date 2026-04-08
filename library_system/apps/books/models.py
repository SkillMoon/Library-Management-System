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
    cover_image = models.ImageField(
        upload_to='covers/',
        null=True,
        blank=True,
        verbose_name='تصویر جلد'
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
        return self.copies.filter(is_available=True).count()


class BookCopy(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='copies',
        verbose_name='کتاب'
    )
    is_available = models.BooleanField(default=True, verbose_name='موجود')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نسخه کتاب'
        verbose_name_plural = 'نسخه‌های کتاب'
        db_table = 'book_copies'

    def __str__(self):
        return f"نسخه {self.id} از {self.book.title}"
