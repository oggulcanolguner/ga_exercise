from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from users import views

urlpatterns = [
    url(r"^sign-up/$", views.SignUpView.as_view(), name="sign_up"),
    url(r"^me/$", views.ProfileView.as_view(), name="profile"),
    url(r"^token/refresh/$", views.JWTRefreshView.as_view(), name="token_refresh",),
    url(r"^token/$", views.JWTObtainPairView.as_view(), name="token_obtain_pair"),
    url(r"^search/$", views.SearchUserView.as_view(), name="search_user"),
]
