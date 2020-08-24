from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from utils.error import not_found_view

handler404 = not_found_view
urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/", include("ga_exercise.urls")),
]
