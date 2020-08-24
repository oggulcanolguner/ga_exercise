from functools import wraps

from django.core.cache import cache
from rest_framework.response import Response

__all__ = ["cache_method", "invalidate_profile_cache"]


def get_user_cache_key(view) -> str:
    return (
        str(view.request.user.id) if view.request.user.is_authenticated else "anonymous"
    )


CACHE_ARGUMENTS = {"user": get_user_cache_key}


CACHE_KEY_DEFAULT = "CACHE_KEY_{function}{arg}"


def cache_method(arg_getters=list):
    def decorator(func):
        @wraps(func)
        def wrapper(view, *args, **kwargs):
            cache_args = ""
            for arg in CACHE_ARGUMENTS:
                if arg in arg_getters:
                    cache_function = CACHE_ARGUMENTS[arg]
                    cache_args += "_" + cache_function(view)
            cache_key = CACHE_KEY_DEFAULT.format(
                function=func.__qualname__, arg=cache_args
            )
            cached_resp = cache.get(cache_key, [])

            if cached_resp:
                return Response(cached_resp)
            main_function = func(view, *args, **kwargs)
            cache.set(cache_key, main_function.data, timeout=None)
            return main_function

        return wrapper

    return decorator


def invalidate_profile_cache(user_id: int) -> None:
    cache_key = CACHE_KEY_DEFAULT.format(function="ProfileView.get", arg=user_id)
    cache.delete(cache_key)
