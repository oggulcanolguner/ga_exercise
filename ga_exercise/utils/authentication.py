from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from utils.error import ApiError, ApiErrorCodes

__all__ = ["CustomJWTAuthentication", "CustomSessionAuthentication"]


class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        try:
            return super().get_validated_token(raw_token)
        except InvalidToken:
            raise ApiError(
                message="Given token not valid for any token type",
                error_code=ApiErrorCodes.GENERIC_INVALID_TOKEN,
                status_code=403,
            )


class CustomSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        if not request.path.startswith(settings.ADMIN_URL):
            return None
        return super().authenticate(request)
