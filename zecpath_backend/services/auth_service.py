from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User


def authenticate_by_email(email, password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist as exc:
        raise AuthenticationFailed("Invalid email or password.") from exc

    authenticated_user = authenticate(
        username=user.username,
        password=password,
    )
    if authenticated_user is None:
        raise AuthenticationFailed("Invalid email or password.")

    return authenticated_user


def issue_token_pair(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
