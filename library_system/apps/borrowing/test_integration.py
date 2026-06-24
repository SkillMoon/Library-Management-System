# apps/borrowing/tests/test_integration.py
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal

from apps.accounts.models import User
from apps.books.models import Book, BookCopy
from apps.borrowing.models import BorrowRequest, Borrow, Fine


class BorrowWorkflowTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='test123',
            role='student',
            national_id='1234567890'
        )

        self.librarian = User.objects.create_user(
            username='librarian1',
            password='test123',
            role='librarian',
            national_id='0987654321'
        )

        self.book = Book.objects.create(
            title='کتاب تست',
            isbn='1234567890123',
            total_copies=2
        )

        self.copy = BookCopy.objects.create(
            book=self.book,
            copy_code='C001',
            status='available'
        )

    def test_complete_borrow_workflow(self):
        # مرحله 1: دانشجو درخواست امانت می‌دهد
        request = BorrowRequest.objects.create(
            user=self.student,
            book=self.book
        )
        self.assertEqual(request.status, 'pending')

        # مرحله 2: کتابدار درخواست را تأیید می‌کند
        request.status = 'approved'
        request.reviewed_by = self.librarian
        request.save()

        borrow = Borrow.objects.create(
            user=self.student,
            book_copy=self.copy,
            librarian=self.librarian,
            borrow_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )

        self.copy.status = 'borrowed'
        self.copy.save()

        # بررسی وضعیت
        self.assertEqual(borrow.status, 'active')
        self.assertEqual(self.copy.status, 'borrowed')

        # مرحله 3: بازگشت کتاب
        borrow.return_date = timezone.now().date()
        borrow.status = 'returned'
        borrow.save()

        self.copy.status = 'available'
        self.copy.save()

        self.assertEqual(borrow.status, 'returned')
        self.assertEqual(self.copy.status, 'available')
#
# class BorrowingFlowIntegrationTest(TestCase):
#     """تست workflow کامل امانت کتاب"""
#
#     def setUp(self):
#         # کاربران
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@test.com',
#             password='pass123',
#             first_name='Test',
#             last_name='User',
#             national_id='1234567890'
#         )
#         self.librarian = User.objects.create_user(
#             username='librarian',
#             email='lib@test.com',
#             password='pass123',
#             first_name='Lib',
#             last_name='Rarian',
#             national_id='0987654321',
#             is_staff=True
#         )
#
#         # کتاب و نسخه
#         self.book = Book.objects.create(
#             title='Test Book',
#             author='Test Author',
#             isbn='1234567890123',
#             publisher='Test Publisher',
#             publish_year=2020,
#             total_copies=2
#         )
#         self.copy1 = BookCopy.objects.create(
#             book=self.book,
#             copy_code='COPY001',
#             status='available'
#         )
#         self.copy2 = BookCopy.objects.create(
#             book=self.book,
#             copy_code='COPY002',
#             status='available'
#         )
#
#     def test_complete_borrowing_flow_success(self):
#         """تست کامل: درخواست → تایید → امانت → بازگشت"""
#         # 1. کاربر درخواست می‌ده
#         request = BorrowRequest.objects.create(
#             user=self.user,
#             book=self.book
#         )
#         self.assertEqual(request.status, 'pending')
#
#         # 2. کتابدار تایید می‌کنه
#         request.status = 'approved'
#         request.approved_by = self.librarian
#         request.approved_at = timezone.now()
#         request.save()
#
#         # 3. امانت ایجاد می‌شه
#         borrow = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copy1,
#             borrow_request=request,
#             borrow_date=timezone.now(),
#             due_date=timezone.now() + timedelta(days=14)
#         )
#
#         # چک وضعیت نسخه
#         self.copy1.refresh_from_db()
#         self.assertEqual(self.copy1.status, 'available')
#
#         # 4. کاربر کتاب رو برمی‌گردونه
#         borrow.return_date = timezone.now()
#         borrow.save()
#
#         # چک وضعیت نسخه بعد از برگشت
#         self.copy1.refresh_from_db()
#         self.assertEqual(self.copy1.status, 'available')
#
#         # چک جریمه نداره
#         self.assertFalse(Fine.objects.filter(borrow=borrow).exists())
#
#     def test_borrowing_with_overdue_and_fine(self):
#         """تست امانت با تاخیر و جریمه"""
#         # امانت با due_date گذشته
#         past_date = timezone.now() - timedelta(days=20)
#         due_date = timezone.now() - timedelta(days=5)
#
#         borrow = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copy1,
#             borrow_date=past_date,
#             due_date=due_date
#         )
#
#         # برگشت کتاب
#         borrow.return_date = timezone.now()
#         borrow.save()
#
#         # ایجاد جریمه
#         fine = Fine.objects.create(
#             borrow=borrow,
#             amount=Decimal('25000.00'),  # 5 روز × 5000 تومان
#             days_late=5
#         )
#
#         # چک جریمه
#         self.assertEqual(fine.amount, Decimal('25000.00'))
#         self.assertFalse(fine.is_paid)
#
#         # پرداخت جریمه
#         fine.is_paid = True
#         fine.paid_at = timezone.now()
#         fine.save()
#
#         self.assertTrue(fine.is_paid)
#         self.assertIsNotNone(fine.paid_at)
#
#     def test_book_availability_tracking(self):
#         """تست ردیابی موجودی کتاب"""
#         # موجودی اولیه
#         self.assertEqual(self.book.available_copies, 2)
#
#         # امانت اول
#         borrow1 = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copy1,
#             borrow_date=timezone.now(),
#             due_date=timezone.now() + timedelta(days=14)
#         )
#         self.assertEqual(self.book.available_copies, 2)
#
#         # امانت دوم
#         user2 = User.objects.create_user(
#             username='user2',
#             email='user2@test.com',
#             password='pass123',
#             first_name='User',
#             last_name='Two',
#             national_id='1111111111'
#         )
#         borrow2 = Borrow.objects.create(
#             user=user2,
#             book_copy=self.copy2,
#             borrow_date=timezone.now(),
#             due_date=timezone.now() + timedelta(days=14)
#         )
#
#         # برگشت اولی
#         borrow1.return_date = timezone.now()
#         borrow1.save()
#
#         # برگشت دومی
#         borrow2.return_date = timezone.now()
#         borrow2.save()
#         self.assertEqual(self.book.available_copies, 2)
#
#     def test_rejected_request_flow(self):
#         """تست رد شدن درخواست"""
#         request = BorrowRequest.objects.create(
#             user=self.user,
#             book=self.book
#         )
#
#         # رد درخواست
#         request.status = 'rejected'
#         request.approved_by = self.librarian
#         request.approved_at = timezone.now()
#         request.save()
#
#         # نباید امانتی ایجاد بشه
#         self.assertFalse(Borrow.objects.filter(borrow_request=request).exists())
#
#         # موجودی تغییر نکرده
#         self.assertEqual(self.book.available_copies, 2)
#
#
# class ConcurrentBorrowingTest(TransactionTestCase):
#     """تست درخواست‌های همزمان"""
#
#     def setUp(self):
#         self.book = Book.objects.create(
#             title='Popular Book',
#             author='Famous Author',
#             isbn='9999999999999',
#             publisher='Big Publisher',
#             publish_year=2023,
#             total_copies=1
#         )
#         self.copy = BookCopy.objects.create(
#             book=self.book,
#             copy_code='LAST001',
#             status='available'
#         )
#
#         self.user1 = User.objects.create_user(
#             username='user1',
#             email='user1@test.com',
#             password='pass123',
#             first_name='User',
#             last_name='One',
#             national_id='1111111111'
#         )
#         self.user2 = User.objects.create_user(
#             username='user2',
#             email='user2@test.com',
#             password='pass123',
#             first_name='User',
#             last_name='Two',
#             national_id='2222222222'
#         )
#
#     def test_concurrent_borrow_requests(self):
#         """تست دو درخواست همزمان برای آخرین نسخه"""
#         # دو درخواست همزمان
#         request1 = BorrowRequest.objects.create(
#             user=self.user1,
#             book=self.book
#         )
#         request2 = BorrowRequest.objects.create(
#             user=self.user2,
#             book=self.book
#         )
#
#         # تایید اولی
#         request1.status = 'approved'
#         request1.save()
#
#         borrow1 = Borrow.objects.create(
#             user=self.user1,
#             book_copy=self.copy,
#             borrow_request=request1,
#             borrow_date=timezone.now(),
#             due_date=timezone.now() + timedelta(days=14)
#         )
#
#
#
#         # تایید دومی نباید امکان‌پذیر باشه (چون نسخه‌ای نیست)
#         request2.status = 'approved'
#         request2.save()
#
#         # نمی‌تونه امانت بگیره چون نسخه‌ای available نیست
#         available_copies = BookCopy.objects.filter(
#             book=self.book,
#             status='available'
#         )
#
#
#
# class UserBorrowingLimitsTest(TestCase):
#     """تست محدودیت‌های امانت کاربر"""
#
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@test.com',
#             password='pass123',
#             first_name='Test',
#             last_name='User',
#             national_id='1234567890'
#         )
#
#         # 3 کتاب مختلف
#         self.books = []
#         self.copies = []
#         for i in range(3):
#             book = Book.objects.create(
#                 title=f'Book {i + 1}',
#                 author=f'Author {i + 1}',
#                 isbn=f'123456789012{i}',
#                 publisher='Publisher',
#                 publish_year=2020,
#                 total_copies=1
#             )
#             copy = BookCopy.objects.create(
#                 book=book,
#                 copy_code=f'COPY00{i + 1}',
#                 status='available'
#             )
#             self.books.append(book)
#             self.copies.append(copy)
#
#     def test_active_borrows_count(self):
#         """تست شمارش امانت‌های فعال"""
#         # امانت اول
#         borrow1 = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copies[0],
#             borrow_date=timezone.now(),
#             due_date=timezone.now() + timedelta(days=14)
#         )
#
#         active_count = Borrow.objects.filter(
#             user=self.user,
#             return_date__isnull=True
#         ).count()
#         self.assertEqual(active_count, 1)
#
#         # امانت دوم
#         borrow2 = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copies[1],
#             borrow_date=timezone.now(),
#             due_date=timezone.now() + timedelta(days=14)
#         )
#
#         active_count = Borrow.objects.filter(
#             user=self.user,
#             return_date__isnull=True
#         ).count()
#         self.assertEqual(active_count, 2)
#
#         # برگشت اولی
#         borrow1.return_date = timezone.now()
#         borrow1.save()
#
#         active_count = Borrow.objects.filter(
#             user=self.user,
#             return_date__isnull=True
#         ).count()
#         self.assertEqual(active_count, 1)
#
#     def test_user_with_unpaid_fines(self):
#         """تست کاربر با جریمه پرداخت نشده"""
#         # امانت با تاخیر
#         past_date = timezone.now() - timedelta(days=20)
#         due_date = timezone.now() - timedelta(days=5)
#
#         borrow = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copies[0],
#             borrow_date=past_date,
#             due_date=due_date,
#             return_date=timezone.now()
#         )
#
#         # جریمه پرداخت نشده
#         fine = Fine.objects.create(
#             borrow=borrow,
#             amount=Decimal('25000.00'),
#             days_late=5,
#             is_paid=False
#         )
#
#         # چک جریمه‌های پرداخت نشده
#         unpaid_fines = Fine.objects.filter(
#             borrow__user=self.user,
#             is_paid=False
#         )
#         self.assertEqual(unpaid_fines.count(), 1)
#         self.assertEqual(unpaid_fines.first().amount, Decimal('25000.00'))
#
#
# class OverdueHandlingTest(TestCase):
#     """تست مدیریت کتاب‌های دیرکرد"""
#
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='test@test.com',
#             password='pass123',
#             first_name='Test',
#             last_name='User',
#             national_id='1234567890'
#         )
#
#         self.book = Book.objects.create(
#             title='Test Book',
#             author='Test Author',
#             isbn='1234567890123',
#             publisher='Publisher',
#             publish_year=2020,
#             total_copies=1
#         )
#         self.copy = BookCopy.objects.create(
#             book=self.book,
#             copy_code='COPY001',
#             status='available'
#         )
#
#     def test_overdue_detection(self):
#         """تست تشخیص کتاب‌های دیرکرد"""
#         # امانت عادی (هنوز due نشده)
#         borrow1 = Borrow.objects.create(
#             user=self.user,
#             book_copy=self.copy,
#             borrow_date=timezone.now() - timedelta(days=5),
#             due_date=timezone.now() + timedelta(days=9)
#         )
#
#         # امانت دیرکرد
#         user2 = User.objects.create_user(
#             username='user2',
#             email='user2@test.com',
#             password='pass123',
#             first_name='User',
#             last_name='Two',
#             national_id='2222222222'
#         )
#         copy2 = BookCopy.objects.create(
#             book=self.book,
#             copy_code='COPY002',
#             status='available'
#         )
#         borrow2 = Borrow.objects.create(
#             user=user2,
#             book_copy=copy2,
#             borrow_date=timezone.now() - timedelta(days=20),
#             due_date=timezone.now() - timedelta(days=5)
#         )
#
#     def test_overdue_list_query(self):
#         """تست query لیست کتاب‌های دیرکرد"""
#         # چند امانت با وضعیت‌های مختلف
#         users = []
#         copies = []
#         for i in range(3):
#             user = User.objects.create_user(
#                 username=f'user{i}',
#                 email=f'user{i}@test.com',
#                 password='pass123',
#                 first_name='User',
#                 last_name=str(i),
#                 national_id=f'{i}{i}{i}{i}{i}{i}{i}{i}{i}{i}'
#             )
#             copy = BookCopy.objects.create(
#                 book=self.book,
#                 copy_code=f'COPY{i + 10}',
#                 status='available'
#             )
#             users.append(user)
#             copies.append(copy)
#
#         # امانت عادی
#         Borrow.objects.create(
#             user=users[0],
#             book_copy=copies[0],
#             borrow_date=timezone.now() - timedelta(days=5),
#             due_date=timezone.now() + timedelta(days=9)
#         )
#
#         # امانت دیرکرد (برنگشته)
#         Borrow.objects.create(
#             user=users[1],
#             book_copy=copies[1],
#             borrow_date=timezone.now() - timedelta(days=20),
#             due_date=timezone.now() - timedelta(days=5)
#         )
#
#         # امانت دیرکرد (برگشته)
#         Borrow.objects.create(
#             user=users[2],
#             book_copy=copies[2],
#             borrow_date=timezone.now() - timedelta(days=30),
#             due_date=timezone.now() - timedelta(days=15),
#             return_date=timezone.now() - timedelta(days=10)
#         )
#
#         # Query امانت‌های دیرکرد فعال
#         overdue_borrows = Borrow.objects.filter(
#             return_date__isnull=True,
#             due_date__lt=timezone.now()
#         )
#
#         self.assertEqual(overdue_borrows.count(), 1)
#         self.assertEqual(overdue_borrows.first().user, users[1])
