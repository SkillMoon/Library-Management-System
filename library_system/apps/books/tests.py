from django.test import TestCase
from .models import Book, BookCopy


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title='تست کتاب',
            author='نویسنده تست',
            isbn='1234567890123',
            subject='علوم کامپیوتر',
            publisher='انتشارات تست',
            publish_year=2024,
            total_copies=5
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'تست کتاب')
        self.assertEqual(self.book.total_copies, 5)

    def test_available_copies_count(self):
        BookCopy.objects.create(book=self.book, copy_code='C001', status='available')
        BookCopy.objects.create(book=self.book, copy_code='C002', status='borrowed')
        BookCopy.objects.create(book=self.book, copy_code='C003', status='available')

        self.assertEqual(self.book.available_copies_count(), 2)

