from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path(r"users/", include(("users.urls", "users"), namespace="users")),
]
