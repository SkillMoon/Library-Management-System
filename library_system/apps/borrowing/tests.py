# apps/borrowing/tests/test_models.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.books.models import Book, BookCopy
from apps.borrowing.models import BorrowRequest, Borrow, Fine


class BorrowRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass')
        self.book = Book.objects.create(title='کتاب', author='نویسنده', isbn='1111111111111')
        self.request = BorrowRequest.objects.create(
            user=self.user,
            book=self.book,
            status=BorrowRequest.Status.PENDING
        )

    def test_request_creation(self):
        self.assertEqual(self.request.user, self.user)
        self.assertEqual(self.request.book, self.book)
        self.assertEqual(self.request.status, BorrowRequest.Status.PENDING)

    def test_request_str(self):
        self.assertIn('student', str(self.request))
        self.assertIn('کتاب', str(self.request))

    def test_status_change(self):
        self.request.status = BorrowRequest.Status.APPROVED
        self.request.save()
        self.assertEqual(self.request.status, BorrowRequest.Status.APPROVED)


class BorrowModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass')
        self.librarian = User.objects.create_user(username='librarian', password='pass', role=User.Role.LIBRARIAN)
        self.book = Book.objects.create(title='کتاب', author='نویسنده', isbn='2222222222222')
        self.copy = BookCopy.objects.create(book=self.book, copy_code='C001')

        self.borrow = Borrow.objects.create(
            user=self.user,
            book_copy=self.copy,
            librarian=self.librarian,
            borrow_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )

    def test_borrow_creation(self):
        self.assertEqual(self.borrow.user, self.user)
        self.assertEqual(self.borrow.book_copy, self.copy)
        self.assertEqual(self.borrow.status, Borrow.Status.ACTIVE)

    def test_borrow_str(self):
        self.assertIn('student', str(self.borrow))

    def test_is_overdue_false(self):
        self.assertFalse(self.borrow.is_overdue)

    def test_is_overdue_true(self):
        self.borrow.due_date = timezone.now().date() - timedelta(days=5)
        self.borrow.save()
        self.assertTrue(self.borrow.is_overdue)

    def test_is_overdue_returned(self):
        self.borrow.status = Borrow.Status.RETURNED
        self.borrow.return_date = timezone.now().date()
        self.borrow.due_date = timezone.now().date() - timedelta(days=5)
        self.borrow.save()
        self.assertFalse(self.borrow.is_overdue)

    def test_overdue_days_zero(self):
        self.assertEqual(self.borrow.overdue_days, 0)

    def test_overdue_days_positive(self):
        self.borrow.due_date = timezone.now().date() - timedelta(days=3)
        self.borrow.save()
        self.assertEqual(self.borrow.overdue_days, 3)

    def test_overdue_days_returned(self):
        self.borrow.due_date = timezone.now().date() - timedelta(days=5)
        self.borrow.return_date = timezone.now().date() - timedelta(days=2)
        self.borrow.status = Borrow.Status.RETURNED
        self.borrow.save()
        self.assertEqual(self.borrow.overdue_days, 3)


class FineModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass')
        self.book = Book.objects.create(title='کتاب', author='نویسنده', isbn='3333333333333')
        self.copy = BookCopy.objects.create(book=self.book, copy_code='C002')
        self.borrow = Borrow.objects.create(
            user=self.user,
            book_copy=self.copy,
            borrow_date=timezone.now().date() - timedelta(days=20),
            due_date=timezone.now().date() - timedelta(days=5)
        )
        self.fine = Fine.objects.create(
            borrow=self.borrow,
            amount=50000,
            days_late=5
        )

    def test_fine_creation(self):
        self.assertEqual(self.fine.borrow, self.borrow)
        self.assertEqual(self.fine.amount, 50000)
        self.assertEqual(self.fine.days_late, 5)
        self.assertFalse(self.fine.is_paid)

    def test_fine_str(self):
        self.assertIn('50,000', str(self.fine))

    def test_fine_payment(self):
        self.fine.is_paid = True
        self.fine.paid_at = timezone.now()
        self.fine.save()
        self.assertTrue(self.fine.is_paid)
        self.assertIsNotNone(self.fine.paid_at)

    def test_one_to_one_constraint(self):
        with self.assertRaises(Exception):
            Fine.objects.create(
                borrow=self.borrow,
                amount=10000,
                days_late=1
            )
