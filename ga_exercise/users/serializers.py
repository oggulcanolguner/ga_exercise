from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users import models
from utils.error import ApiError, ApiErrorCodes


class UserSerializer(serializers.ModelSerializer):

    ERROR_CODE_MAP = {
        ("email", "unique"): ApiErrorCodes.USERS_EMAIL_EXISTS,
        ("username", "unique"): ApiErrorCodes.USERS_EMAIL_EXISTS,
        ("password", "required"): ApiErrorCodes.GENERIC_MISSING_QUERY_PARAMETER,
        ("country", "required"): ApiErrorCodes.GENERIC_MISSING_QUERY_PARAMETER,
        ("username", "required"): ApiErrorCodes.GENERIC_MISSING_QUERY_PARAMETER,
        ("date_of_birth", "required"): ApiErrorCodes.GENERIC_MISSING_QUERY_PARAMETER,
    }
    country = CountryField()

    class Meta:
        model = models.User
        fields = [
            "email",
            "password",
            "username",
            "full_name",
            "date_of_birth",
            "bio",
            "phone",
            "country",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        if data.get("password"):
            try:
                validate_password(data["password"])
            except django_exceptions.ValidationError as e:
                raise ApiError.from_password_validation_error(e)

        super().validate(data)
        return data

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        validated_data.pop("email")
        validated_data.pop("password")
        return self.Meta.model.objects.create_user(email, password, **validated_data)

    def get_api_error(self):
        code = ApiErrorCodes.GENERIC
        message = ""
        for field, error_list in self.errors.items():
            message = str(error_list[0])
            if (field, error_list[0].code) in self.ERROR_CODE_MAP:
                code = self.ERROR_CODE_MAP[field, error_list[0].code]
                if error_list[0].code == "required":
                    message += f" ({field})"
                break
        return ApiError(message=message, error_code=code, status_code=400)


class LoggedInUserSerializer(UserSerializer):
    access = serializers.SerializerMethodField()
    refresh = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["access", "refresh"]

    def get_access(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_refresh(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)


class UserSummarySerializer(UserSerializer):
    class Meta:
        model = models.User
        fields = ["username", "bio", "country"]
