from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from config.views import IndexView, ObjectHistoryView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.v1.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("", IndexView.as_view(), name="index"),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            email_template_name="emails/password_reset.html",
        ),
        name="password_reset",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("user/", include("authn.urls")),
    path(
        "history/<str:app_label>/<str:model_name>/<pk>/",
        ObjectHistoryView.as_view(),
        name="object_history",
    ),
]
