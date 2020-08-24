import traceback

from django.utils.deprecation import MiddlewareMixin
from utils.error import GENERIC_ERROR, ApiError

__all__ = ["ErrorCapturedMiddleware"]


class ErrorCapturedMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if not isinstance(exception, ApiError):
            traceback.print_exc()
            exception = GENERIC_ERROR
        return exception.to_json_response()
