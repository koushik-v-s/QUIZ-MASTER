"""
Custom exception handler for consistent API error responses.
All errors return: {"success": false, "error": {"code": "...", "message": "...", "details": {}}}
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
    NotAuthenticated,
    Throttled,
)
from rest_framework import status
from django.http import Http404


def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps all errors in a consistent format.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        error_code = _get_error_code(exc)
        error_message = _get_error_message(exc, response)
        error_details = _get_error_details(exc, response)

        response.data = {
            'success': False,
            'error': {
                'code': error_code,
                'message': error_message,
                'details': error_details,
            }
        }

    return response


def _get_error_code(exc):
    """Map exception type to a string error code."""
    error_map = {
        ValidationError: 'VALIDATION_ERROR',
        NotFound: 'NOT_FOUND',
        Http404: 'NOT_FOUND',
        PermissionDenied: 'PERMISSION_DENIED',
        AuthenticationFailed: 'AUTHENTICATION_FAILED',
        NotAuthenticated: 'NOT_AUTHENTICATED',
        Throttled: 'RATE_LIMITED',
    }
    for exc_class, code in error_map.items():
        if isinstance(exc, exc_class):
            return code
    if hasattr(exc, 'default_code'):
        return str(exc.default_code).upper()
    return 'SERVER_ERROR'


def _get_error_message(exc, response):
    """Extract a human-readable error message."""
    if isinstance(exc, ValidationError):
        return 'Validation failed. Check the details for more information.'
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        if isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else 'An error occurred.'
    return 'An error occurred.'


def _get_error_details(exc, response):
    """Extract structured error details."""
    if isinstance(exc, ValidationError) and isinstance(exc.detail, dict):
        return exc.detail
    return {}


# ─── Custom Exceptions ───────────────────────────────────────────────

class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable. Please try again later.'
    default_code = 'SERVICE_UNAVAILABLE'


class QuotaExceeded(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'You have exceeded your quota. Please try again later.'
    default_code = 'QUOTA_EXCEEDED'


class AIGenerationError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'AI generation failed. Please try again.'
    default_code = 'AI_GENERATION_ERROR'
