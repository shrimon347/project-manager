from django.conf import settings
from rest_framework import status

from core.responses import success_response


def build_register_response(*, user_payload):
    return success_response(
        message="Registration successful. Verify your email.",
        data={"user": user_payload},
        status_code=status.HTTP_201_CREATED,
    )


def build_login_response(*, access_token, refresh_token):
    response = success_response(
        message="Login successful.",
        data={
            "token_type": "Bearer",
            "access_token": access_token,
        },
        status_code=status.HTTP_200_OK,
    )
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path=settings.AUTH_COOKIE_PATH,
    )
    return response


def build_logout_response():
    response = success_response(
        message="Logout successful.",
        data={},
        status_code=status.HTTP_200_OK,
    )
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    return response


def build_refresh_response(*, access_token, refresh_token):
    response = success_response(
        message="Token refreshed successfully.",
        data={
            "token_type": "Bearer",
            "access_token": access_token,
        },
        status_code=status.HTTP_200_OK,
    )
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path=settings.AUTH_COOKIE_PATH,
    )
    return response


def get_refresh_token_from_request(request):
    payload = request.data.copy()
    cookie_refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if "refresh" not in payload and cookie_refresh:
        payload["refresh"] = cookie_refresh
    return payload
