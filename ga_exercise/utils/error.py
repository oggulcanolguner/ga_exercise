from enum import IntEnum

import ujson
from django.http import HttpRequest, JsonResponse

__all__ = [
    "ApiError",
    "ApiErrorCodes",
    "GENERIC_ERROR",
    "not_found_view",
]


class ApiErrorCodes(IntEnum):

    GENERIC = 10001
    GENERIC_SERIALIZER_VALIDATION_FAILED = 10002
    GENERIC_INVALID_TOKEN = 10003
    GENERIC_INVALID_QUERY_PARAMETER = 10004
    GENERIC_MISSING_QUERY_PARAMETER = 10005
    GENERIC_PAGE_NOT_FOUND = 10006

    USERS_EMAIL_EXISTS = 20001
    USERS_USERNAME_EXISTS = 20002
    USERS_INVALID_CREDENTIALS = 20003
    USERS_TOKEN_NOT_FOUND = 20004
    USER_PASSWORD_TOO_SHORT = 20005
    USER_PASSWORD_TOO_COMMON = 20006
    USER_PASSWORD_ENTIRELY_NUMERIC = 20007


class ApiError(Exception):
    def __init__(self, message, error_code, status_code=500):
        super().__init__()
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {"message": self.message.capitalize(), "code": self.error_code}

    def to_json_response(self) -> JsonResponse:
        return JsonResponse(self.to_dict(), status=self.status_code)

    @classmethod
    def from_response(cls, response) -> object:
        content_json = ujson.loads(response.content)
        return cls(
            message=content_json.get("message"),
            error_code=content_json.get("code"),
            status_code=response.status_code,
        )

    @classmethod
    def from_password_validation_error(cls, validation_error) -> object:
        error = validation_error.error_list[0]
        return cls(
            message=error.message,
            error_code=getattr(ApiErrorCodes, "USER_%s" % error.code.upper()),
            status_code=400,
        )

    @classmethod
    def from_validation_error(cls, validation_error) -> object:
        for field, errors in validation_error.detail.items():
            print("aa")
            return cls(
                message="%s (field: %s)" % (str(errors[0]), field),
                error_code=ApiErrorCodes.GENERIC_SERIALIZER_VALIDATION_FAILED,
                status_code=400,
            )

    def __eq__(self, other):
        if not isinstance(other, ApiError):
            return False
        return all(
            (
                self.message == other.message,
                self.error_code == other.error_code,
                self.status_code == other.status_code,
            )
        )

    def __repr__(self):
        return "%s - %s (%s)" % (self.message, self.error_code, self.status_code,)


GENERIC_ERROR = ApiError(
    message="Critical error occured!", error_code=ApiErrorCodes.GENERIC
)
NOT_FOUND_ERROR = ApiError(
    message="Page not found, check url.",
    error_code=ApiErrorCodes.GENERIC_PAGE_NOT_FOUND,
    status_code=404,
)


def not_found_view(request: HttpRequest, exception=None) -> JsonResponse:
    return NOT_FOUND_ERROR.to_json_response()
