import pytest
from django.core import mail

from authn.emails import make_email_verification_token
from authn.models import User


@pytest.mark.django_db
class TestCreateAccount:
    def test_creates_user_logs_in_and_sends_verification(self, client):
        response = client.post(
            "/user/create/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "StrongPass1!",
                "password2": "StrongPass1!",
            },
        )
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()
        assert len(mail.outbox) == 1
        assert "verify" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
class TestVerifyEmail:
    def test_valid_token_verifies_and_redirects(self, client, user):
        token = make_email_verification_token(user)
        response = client.get(f"/user/verify-email/{token}/")
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.email_verified

    def test_invalid_token_rejected(self, client, user):
        response = client.get("/user/verify-email/bogus/")
        assert response.status_code == 400
        user.refresh_from_db()
        assert not user.email_verified


@pytest.mark.django_db
class TestProfile:
    def test_requires_login(self, client):
        response = client.get("/user/profile/")
        assert response.status_code == 302

    def test_renders_for_logged_in_user(self, client, user):
        client.force_login(user)
        response = client.get("/user/profile/")
        assert response.status_code == 200

    def test_email_change_sends_verification(self, client, user):
        client.force_login(user)
        response = client.post(
            "/user/profile/edit",
            {"username": user.username, "email": "changed@example.com"},
        )
        assert response.status_code == 302
        user.refresh_from_db()
        assert not user.email_verified
        assert len(mail.outbox) == 1
