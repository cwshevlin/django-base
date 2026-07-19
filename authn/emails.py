"""Email-verification tokens, in one place for both the web and API flows."""

from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

EMAIL_VERIFICATION_SALT = "email-verification"
EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24  # 24 hours


def make_email_verification_token(user):
    return signing.dumps(
        {"user_id": str(user.pk), "email": user.email},
        salt=EMAIL_VERIFICATION_SALT,
    )


def check_email_verification_token(token):
    """Return the user the token was issued for.

    Raises ``signing.SignatureExpired``, ``signing.BadSignature``, or
    ``User.DoesNotExist`` for the caller to map to a response.
    """
    from .models import User

    data = signing.loads(
        token, salt=EMAIL_VERIFICATION_SALT, max_age=EMAIL_VERIFICATION_MAX_AGE
    )
    return User.objects.get(pk=data["user_id"], email=data["email"])


def send_verification_email(user, request=None):
    """Send a verification link (web flow, when ``request`` is given) or a raw
    token for clients to POST to the API (API flow)."""
    token = make_email_verification_token(user)
    if request is not None:
        verification_url = request.build_absolute_uri(
            reverse("verify_email", kwargs={"token": token})
        )
        message = (
            "Click the link below to verify your email address:\n\n"
            f"{verification_url}\n\nThis link expires in 24 hours."
        )
    else:
        message = (
            "Use the token below to verify your email address:\n\n"
            f"{token}\n\nThis token expires in 24 hours."
        )
    send_mail(
        subject="Verify your email address",
        message=message,
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
    )
