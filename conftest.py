import pytest

from authn.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", password="testpass", email="testuser@example.com"
    )
