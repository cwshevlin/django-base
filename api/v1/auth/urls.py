from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, MeView, RegisterView, VerifyEmailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-auth-register"),
    path("login/", LoginView.as_view(), name="api-auth-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("verify-email/", VerifyEmailView.as_view(), name="api-auth-verify-email"),
    path("me/", MeView.as_view(), name="api-auth-me"),
]
