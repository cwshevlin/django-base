from auditlog.registry import auditlog
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from config.models import UUIDTimeStampedModel


class User(AbstractUser, UUIDTimeStampedModel):
    email_verified = models.BooleanField(default=False)
    avatar_url = models.URLField(max_length=1024, blank=True, null=True)
    phone_number = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )

    # Only affects creation of a user from the createsuperuser method, not from any other part of the app.
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return self.username


auditlog.register(
    User, exclude_fields=["created_at", "updated_at", "last_login", "password"]
)
