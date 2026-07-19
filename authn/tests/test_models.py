import pytest
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType


@pytest.mark.django_db
class TestUser:
    def test_pk_is_uuid7(self, user):
        assert user.pk.version == 7

    def test_timestamps_set(self, user):
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_str(self, user):
        assert str(user) == "testuser"

    def test_changes_are_audit_logged(self, user):
        user.first_name = "Changed"
        user.save()
        ct = ContentType.objects.get_for_model(user)
        assert LogEntry.objects.filter(content_type=ct, object_pk=str(user.pk)).exists()
