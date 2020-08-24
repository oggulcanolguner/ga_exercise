from .base import *  # noqa
from .base import env

ENVIRONMENT = Environment.LOCAL

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# django-extensions
INSTALLED_APPS += ["django_extensions"]

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
