from django.urls import path

from .views import CreateAccountView, ProfileEditView, ProfileView, VerifyEmailView

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit", ProfileEditView.as_view(), name="profile_edit"),
    path("create/", CreateAccountView.as_view(), name="create_account"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
]
