from datetime import datetime

from rest_framework.test import APITestCase
from users import models, serializers
from utils.error import ApiError, ApiErrorCodes

__all__ = ["UserSerializerTestCase"]


class DummyMock:
    def __init__(self):
        pass

    def __eq__(self, other):
        return True


class UserSerializerTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.data = {
            "email": "user@test.com",
            "password": "test12345",
            "username": "testuser",
            "date_of_birth": "1988-10-10",
            "full_name": "Test User",
            "country": "TR",
            "phone": "+9055555555",
            "bio": "tester",
        }
        self.user = models.User.objects.create_user(
            email="test@test.com",
            password="superpassword123",
            username="tester12",
            date_of_birth="1977-12-2",
        )

    def test_validated_data(self):
        serializer = serializers.UserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        _data = self.data
        _data["date_of_birth"] = datetime.strptime(
            _data["date_of_birth"], "%Y-%m-%d"
        ).date()
        self.assertEqual(dict(serializer.validated_data), _data)

    def test_user_create(self):
        models.User.objects.all().delete()
        serializer = serializers.UserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.create(serializer.validated_data)
        self.assertEqual(user, models.User.objects.first())
        self.assertEqual(user.email, self.data["email"])
        self.assertEqual(user.username, self.data["username"])
        self.assertEqual(user.full_name, self.data["full_name"])

    def test_user_create_already_exists(self):
        _data = self.data
        _data["email"] = self.user.email
        serializer = serializers.UserSerializer(data=_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.get_api_error(), self._get_email_exists_error())

    def test_field_required(self):
        _data = self.data
        _data.pop("username")
        serializer = serializers.UserSerializer(data=_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.get_api_error(), self._get_field_required_error())

    def test_username_invalid(self):
        _data = self.data
        _data["username"] = "testuser$%$#"
        serializer = serializers.UserSerializer(data=_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.get_api_error().message,
            "Username must contain alphanumeric characters",
        )

    def test_phone_invalid(self):
        _data = self.data
        _data["phone"] = "myphone"
        serializer = serializers.UserSerializer(data=_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.get_api_error().message,
            "The number must be entered in the format: '+999999999' with up to 15 digits.",
        )

    @staticmethod
    def _get_email_exists_error():
        return ApiError(
            message=DummyMock(),
            error_code=ApiErrorCodes.USERS_EMAIL_EXISTS,
            status_code=400,
        )

    @staticmethod
    def _get_field_required_error():
        return ApiError(
            message=DummyMock(),
            error_code=ApiErrorCodes.GENERIC_MISSING_QUERY_PARAMETER,
            status_code=400,
        )
