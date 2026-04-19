from django.conf import settings
from rest_framework import status

from core.responses import success_response


def set_refresh_cookie(*, response, refresh_token):
    """Attach refresh token cookie to response.

    Inputs:
    - response: DRF/Django response object
    - refresh_token: JWT refresh token string

    Outputs:
    - response with refresh cookie set
    """

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


def clear_refresh_cookie(*, response):
    """Remove refresh token cookie from response.

    Inputs:
    - response: DRF/Django response object

    Outputs:
    - response with refresh cookie cleared
    """

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
            "access": access_token,
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
    """Read refresh token from request body or fallback cookie.

    Inputs:
    - request: DRF request object

    Outputs:
    - mutable payload dict containing refresh token when available
    """

    payload = request.data.copy()
    cookie_refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if "refresh" not in payload and cookie_refresh:
        payload["refresh"] = cookie_refresh
    return payload
