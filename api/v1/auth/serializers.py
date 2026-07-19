from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from authn.emails import check_email_verification_token, send_verification_email
from authn.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar_url",
            "phone_number",
            "email_verified",
            "created_at",
        ]
        read_only_fields = ["id", "email_verified", "created_at"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, default="")
    last_name = serializers.CharField(max_length=150, default="")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        data["user"] = user
        return data


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            return check_email_verification_token(value)
        except signing.SignatureExpired:
            raise serializers.ValidationError("This verification link has expired.")
        except (signing.BadSignature, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link.")


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar_url",
            "phone_number",
        ]

    def update(self, instance, validated_data):
        email_changed = (
            "email" in validated_data and validated_data["email"] != instance.email
        )

        instance = super().update(instance, validated_data)

        if email_changed:
            instance.email_verified = False
            instance.save(update_fields=["email_verified"])
            send_verification_email(instance)

        return instance


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
