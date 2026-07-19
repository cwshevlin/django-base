import pytest
from django.template import Context, Template


@pytest.mark.django_db
class TestIndex:
    def test_renders(self, client):
        response = client.get("/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestObjectHistory:
    def test_requires_login(self, client, user):
        response = client.get(f"/history/authn/user/{user.pk}/")
        assert response.status_code == 302

    def test_lists_entries_after_a_change(self, client, user):
        user.first_name = "Changed"
        user.save()
        client.force_login(user)
        response = client.get(f"/history/authn/user/{user.pk}/")
        assert response.status_code == 200
        assert b"first_name" in response.content


class TestMessageBox:
    def test_renders_level_markup(self):
        template = Template(
            "{% load messages %}"
            "{% message_box level='success' %}Saved.{% endmessage_box %}"
        )
        rendered = template.render(Context())
        assert "message-box-success" in rendered
        assert "Saved." in rendered
