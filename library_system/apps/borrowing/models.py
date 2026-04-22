from django.db import models
from django.conf import settings
from django.utils import timezone


class BorrowRequest(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'در انتظار تأیید'
        APPROVED = 'approved', 'تأیید شده'
        REJECTED = 'rejected', 'رد شده'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrow_requests',
        verbose_name='کاربر'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='borrow_requests',
        verbose_name='کتاب'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='وضعیت'
    )
    request_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درخواست')
    note = models.TextField(null=True, blank=True, verbose_name='یادداشت')

    class Meta:
        verbose_name = 'درخواست امانت'
        verbose_name_plural = 'درخواست‌های امانت'
        db_table = 'borrow_requests'

    def __str__(self):
        return f"{self.user} — {self.book} ({self.status})"


class Borrow(models.Model):
    class Status(models.TextChoices):
        ACTIVE   = 'active',   'فعال'
        RETURNED = 'returned', 'بازگشت داده شده'
        OVERDUE  = 'overdue',  'تأخیر'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrows',
        verbose_name='امانت‌گیرنده'
    )
    book_copy = models.ForeignKey(
        'books.BookCopy',
        on_delete=models.CASCADE,
        related_name='borrows',
        verbose_name='نسخه کتاب'
    )
    librarian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_borrows',
        verbose_name='کتابدار پردازش‌کننده'
    )
    borrow_request = models.OneToOneField(
        BorrowRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrow',
        verbose_name='درخواست مرتبط'
    )
    borrow_date = models.DateField(default=timezone.now, verbose_name='تاریخ امانت')
    due_date    = models.DateField(verbose_name='تاریخ سررسید')
    return_date = models.DateField(null=True, blank=True, verbose_name='تاریخ بازگشت')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='وضعیت'
    )

    class Meta:
        verbose_name = 'امانت'
        verbose_name_plural = 'امانت‌ها'
        db_table = 'borrows'

    def __str__(self):
        return f"{self.user} — {self.book_copy} — {self.borrow_date}"

    @property
    def is_overdue(self):
        if self.status == self.Status.RETURNED:
            return False
        return timezone.now().date() > self.due_date

    @property
    def overdue_days(self):
        if self.status == self.Status.RETURNED:
            end_date = self.return_date
        else:
            end_date = timezone.now().date()
        delta = (end_date - self.due_date).days
        return max(delta, 0)


class Fine(models.Model):
    borrow = models.OneToOneField(
        Borrow,
        on_delete=models.CASCADE,
        related_name='fine',
        verbose_name='امانت'
    )
    amount    = models.PositiveIntegerField(verbose_name='مبلغ جریمه (ریال)')
    days_late = models.PositiveIntegerField(verbose_name='تعداد روزهای تأخیر')
    is_paid   = models.BooleanField(default=False, verbose_name='پرداخت شده')
    paid_at   = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fines_registered',
        verbose_name='ثبت‌کننده'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'جریمه'
        verbose_name_plural = 'جریمه‌ها'
        db_table = 'fines'

    def __str__(self):
        return f"جریمه امانت {self.borrow.id} — {self.amount:,} ریال"
