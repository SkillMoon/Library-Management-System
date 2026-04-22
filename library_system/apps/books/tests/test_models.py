# apps/books/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.books.models import Book, BookCopy


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            publisher="Test Publisher",
            publish_year=2020,
            category="Fiction",
            description="A test book",
            total_copies=5
        )

    def test_book_creation(self):
        """تست ساخت کتاب"""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.total_copies, 5)

    def test_book_str(self):
        """تست __str__ method"""
        expected = f"{self.book.title} - {self.book.author}"
        self.assertEqual(str(self.book), expected)

    def test_available_copies_no_copies(self):
        """تست available_copies وقتی هیچ BookCopy وجود نداره"""
        self.assertEqual(self.book.available_copies, 0)

    def test_available_copies_with_available_copies(self):
        """تست available_copies با نسخه‌های موجود"""
        BookCopy.objects.create(book=self.book, copy_code="C001", status="available")
        BookCopy.objects.create(book=self.book, copy_code="C002", status="available")
        BookCopy.objects.create(book=self.book, copy_code="C003", status="borrowed")

        self.assertEqual(self.book.available_copies, 2)

    def test_isbn_unique(self):
        """تست unique بودن ISBN"""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Another Book",
                author="Another Author",
                isbn="1234567890123",  # تکراری
                publisher="Test Publisher",
                publish_year=2021,
                total_copies=3
            )

    def test_publish_year_validation(self):
        """تست validation سال انتشار (باید مثبت باشه)"""
        book = Book(
            title="Invalid Year Book",
            author="Test Author",
            isbn="9999999999999",
            publisher="Test Publisher",
            publish_year=-100,
            total_copies=1
        )
        with self.assertRaises(ValidationError):
            book.full_clean()


class BookCopyModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            publisher="Test Publisher",
            publish_year=2020,
            total_copies=3
        )

    def test_book_copy_creation(self):
        """تست ساخت نسخه کتاب"""
        copy = BookCopy.objects.create(
            book=self.book,
            copy_code="C001",
            status="available"
        )
        self.assertEqual(copy.book, self.book)
        self.assertEqual(copy.copy_code, "C001")
        self.assertEqual(copy.status, "available")

    def test_book_copy_str(self):
        """تست __str__ method"""
        copy = BookCopy.objects.create(
            book=self.book,
            copy_code="C001",
            status="available"
        )
        expected = f"{self.book.title} - Copy {copy.copy_code}"
        self.assertEqual(str(copy), expected)

    def test_copy_code_unique_per_book(self):
        """تست unique بودن copy_code برای هر کتاب"""
        BookCopy.objects.create(book=self.book, copy_code="C001", status="available")

        with self.assertRaises(Exception):
            BookCopy.objects.create(book=self.book, copy_code="C001", status="available")

    def test_status_choices(self):
        """تست وضعیت‌های مجاز"""
        copy = BookCopy.objects.create(
            book=self.book,
            copy_code="C001",
            status="available"
        )

        # تست تغییر وضعیت
        copy.status = "borrowed"
        copy.save()
        self.assertEqual(copy.status, "borrowed")

        copy.status = "damaged"
        copy.save()
        self.assertEqual(copy.status, "damaged")

    def test_invalid_status(self):
        """تست وضعیت نامعتبر"""
        copy = BookCopy(
            book=self.book,
            copy_code="C001",
            status="invalid_status"
        )
        with self.assertRaises(ValidationError):
            copy.full_clean()
