from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase
from psycopg2.errors import NotNullViolation


class UsersManagersTests(TestCase):
    def setUp(self) -> None:
        self.email = "normal@user.com"
        self.admin_email = "super@user.com"
        self.password = "password"
        self.date_of_birth = "1979-12-20"
        self.username = "testuser"
        self.admin_username = "admin"

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            date_of_birth=self.date_of_birth,
            username=self.username,
        )
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        User.objects.all().delete()
        with self.assertRaises((TypeError, NotNullViolation, IntegrityError)):
            User.objects.create_user()
        with self.assertRaises((TypeError, ValueError)):
            User.objects.create_user(
                email="", date_of_birth=self.date_of_birth, username=self.username
            )
        with self.assertRaises((TypeError, ValueError)):
            User.objects.create_user(
                email="",
                password=self.password,
                date_of_birth=self.date_of_birth,
                username=self.username,
            )
        with self.assertRaises((NotNullViolation, IntegrityError)):
            User.objects.create_user(email=self.email, password=self.password)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            self.admin_email,
            self.password,
            date_of_birth=self.date_of_birth,
            username=self.admin_username,
        )
        self.assertEqual(admin_user.email, self.admin_email)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com",
                password="foo",
                is_superuser=False,
                date_of_birth=self.date_of_birth,
                username=self.admin_username,
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=self.admin_email,
                password=self.password,
                is_staff=False,
                date_of_birth=self.date_of_birth,
                username=self.admin_username,
            )
