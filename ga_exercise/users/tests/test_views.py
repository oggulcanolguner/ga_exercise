import json

import ujson
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users import models
from utils.error import ApiError, ApiErrorCodes


class JWTObtainPairViewTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = models.User.objects.create_user(
            email="test@test.com",
            password="superpassword123",
            username="tester12",
            date_of_birth="1977-12-2",
        )
        self.password = "superpassword123"
        self.data = {
            "email": self.user.email,
            "password": self.password,
        }
        self.login_error = ApiError(
            message="No active account found with the given credentials",
            error_code=ApiErrorCodes.USERS_INVALID_CREDENTIALS,
            status_code=401,
        )

    def test_success(self):
        response = self.client.post(
            self._get_url(), ujson.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_json = ujson.loads(response.content)
        for field in ["refresh", "access"]:
            self.assertIn(field, response_json)

    def test_invalid_password(self):
        self.data["password"] = "invalid"
        response = self.client.post(
            self._get_url(), ujson.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(ApiError.from_response(response), self.login_error)

    def test_missing_field(self):
        del self.data["email"]
        response = self.client.post(
            self._get_url(), ujson.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def _get_url(self):
        return reverse("users:token_obtain_pair")


class JWTRefreshViewTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = models.User.objects.create_user(
            email="test@test.com",
            password="superpassword123",
            username="tester12",
            date_of_birth="1977-12-2",
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer %s" % str(self.token.access_token)
        )
        self.url = reverse("users:token_refresh")
        self.data = {"refresh": str(self.token), "email": self.user.email}
        self.token_error = ApiError(
            message="Token is invalid or expired",
            error_code=ApiErrorCodes.USERS_TOKEN_NOT_FOUND,
            status_code=404,
        )

    def test_success(self):
        response = self.client.post(
            self.url, ujson.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_json = ujson.loads(response.content)
        self.assertIn("access", response_json)

    def test_invalid_token(self):
        self.data["refresh"] = "invalid"
        response = self.client.post(
            self.url, ujson.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(ApiError.from_response(response), self.token_error)
