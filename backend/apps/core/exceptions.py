"""
Custom exception handler for consistent API error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error responses.

    Response format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {} or []  (optional field-level errors)
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            'success': False,
            'error': {
                'code': _get_error_code(response.status_code),
                'message': _get_error_message(exc, response),
                'details': response.data if isinstance(response.data, (dict, list)) else {'detail': response.data},
            }
        }
        response.data = error_payload
        return response

    # Handle Django ValidationError (not caught by DRF)
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Validation failed.',
                    'details': exc.message_dict if hasattr(exc, 'message_dict') else {'detail': exc.messages},
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def _get_error_code(status_code):
    """Map HTTP status codes to error codes."""
    codes = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        409: 'CONFLICT',
        429: 'RATE_LIMIT_EXCEEDED',
        500: 'INTERNAL_SERVER_ERROR',
    }
    return codes.get(status_code, 'ERROR')


def _get_error_message(exc, response):
    """Extract a human-readable message from the exception."""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        if isinstance(exc.detail, list) and len(exc.detail) > 0:
            return str(exc.detail[0])
    return f'Request failed with status {response.status_code}.'
