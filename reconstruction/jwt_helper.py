from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from datetime import timedelta


def create_access_token(user_id):
    token = AccessToken()
    token["user_id"] = user_id
    token.set_exp(from_time=None, lifetime=timedelta(seconds=settings.JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()))
    return str(token)


def get_jwt_payload(token):
    try:
        payload = AccessToken(token)
        return payload
    except TokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def get_access_token(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return request.COOKIES.get("access_token")
