import logging
from typing import Any

from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("django.request")


class CustomAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Something went wrong."
    default_code = "error"

    def __init__(self, detail=None, code=None, errors=None):
        super().__init__(detail=detail, code=code)
        self.errors = errors or {}


class NotFoundException(CustomAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class ConflictException(CustomAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists."
    default_code = "conflict"


class UnauthorizedException(CustomAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication failed."
    default_code = "unauthorized"


class ForbiddenException(CustomAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "forbidden"


def _normalize_errors(raw_errors: Any) -> Any:
    if isinstance(raw_errors, dict):
        return {key: _normalize_errors(value) for key, value in raw_errors.items()}
    if isinstance(raw_errors, list):
        return [_normalize_errors(item) for item in raw_errors]
    return force_str(raw_errors)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.error(
            "Unhandled exception in API request.",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred. Please try again.",
                "errors": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        message = "Validation failed."
        errors = _normalize_errors(response.data)
    elif isinstance(exc, CustomAPIException):
        message = force_str(exc.detail)
        errors = _normalize_errors(exc.errors)
    else:
        detail = response.data.get("detail") if isinstance(response.data, dict) else "Request failed."
        message = force_str(detail)
        errors = {}
        if isinstance(response.data, dict):
            errors = _normalize_errors({k: v for k, v in response.data.items() if k != "detail"})

    response.data = {
        "success": False,
        "message": message,
        "code": force_str(getattr(exc, "default_code", "error")),
        "errors": errors,
    }
    return response

