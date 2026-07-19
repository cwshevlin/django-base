import pytest

from authn.emails import make_email_verification_token
from authn.models import User


@pytest.mark.django_db
class TestRegister:
    def test_creates_user_and_returns_tokens(self, client):
        response = client.post(
            "/api/v1/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "StrongPass1!",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert "tokens" in data
        assert "access" in data["tokens"]
        assert "refresh" in data["tokens"]
        assert data["user"]["username"] == "newuser"
        assert User.objects.filter(username="newuser").exists()

    def test_duplicate_username_rejected(self, client, user):
        response = client.post(
            "/api/v1/auth/register/",
            {
                "username": user.username,
                "email": "other@example.com",
                "password": "StrongPass1!",
            },
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_weak_password_rejected(self, client):
        response = client.post(
            "/api/v1/auth/register/",
            {"username": "weakuser", "email": "weak@example.com", "password": "123"},
            content_type="application/json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_valid_credentials_return_tokens(self, client, user):
        response = client.post(
            "/api/v1/auth/login/",
            {"username": user.username, "password": "testpass"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert "access" in data["tokens"]

    def test_invalid_credentials_rejected(self, client, user):
        response = client.post(
            "/api/v1/auth/login/",
            {"username": user.username, "password": "wrongpass"},
            content_type="application/json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestMe:
    def _auth_header(self, client, user):
        resp = client.post(
            "/api/v1/auth/login/",
            {"username": user.username, "password": "testpass"},
            content_type="application/json",
        )
        token = resp.json()["tokens"]["access"]
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_get_profile(self, client, user):
        headers = self._auth_header(client, user)
        response = client.get("/api/v1/auth/me/", **headers)
        assert response.status_code == 200
        assert response.json()["username"] == user.username

    def test_unauthenticated_rejected(self, client):
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 401

    def test_patch_profile(self, client, user):
        headers = self._auth_header(client, user)
        response = client.patch(
            "/api/v1/auth/me/",
            {"first_name": "Updated"},
            content_type="application/json",
            **headers,
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"


@pytest.mark.django_db
class TestVerifyEmail:
    def test_valid_token_verifies_email(self, client, user):
        token = make_email_verification_token(user)
        response = client.post(
            "/api/v1/auth/verify-email/",
            {"token": token},
            content_type="application/json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email_verified

    def test_bad_token_rejected(self, client, user):
        response = client.post(
            "/api/v1/auth/verify-email/",
            {"token": "not-a-real-token"},
            content_type="application/json",
        )
        assert response.status_code == 400
        user.refresh_from_db()
        assert not user.email_verified
