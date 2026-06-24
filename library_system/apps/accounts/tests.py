# apps/accounts/tests/test_models.py
from django.test import TestCase
from apps.accounts.models import User, ImportLog


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='علی',
            last_name='احمدی',
            role=User.Role.STUDENT,
            national_id='1234567890',
            phone='09123456789'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, User.Role.STUDENT)
        self.assertEqual(self.user.national_id, '1234567890')
        self.assertTrue(self.user.is_active)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'علی احمدی (student)')

    def test_national_id_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                password='pass',
                national_id='1234567890'
            )

    def test_role_choices(self):
        self.user.role = User.Role.LIBRARIAN
        self.user.save()
        self.assertEqual(self.user.role, User.Role.LIBRARIAN)

    def test_default_role(self):
        user2 = User.objects.create_user(username='user2', password='pass')
        self.assertEqual(user2.role, User.Role.STUDENT)


class ImportLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='librarian',
            password='pass',
            role=User.Role.LIBRARIAN
        )
        self.log = ImportLog.objects.create(
            imported_by=self.user,
            file_name='books.csv',
            total_rows=100,
            success_count=95,
            fail_count=5,
            errors='خطا در ردیف 10، 20، 30'
        )

    def test_log_creation(self):
        self.assertEqual(self.log.file_name, 'books.csv')
        self.assertEqual(self.log.total_rows, 100)
        self.assertEqual(self.log.success_count, 95)
        self.assertEqual(self.log.fail_count, 5)

    def test_log_str(self):
        self.assertIn('books.csv', str(self.log))

    def test_user_deletion_sets_null(self):
        user_id = self.user.id
        self.user.delete()
        self.log.refresh_from_db()
        self.assertIsNone(self.log.imported_by)
