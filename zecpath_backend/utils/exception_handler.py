import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Day 13 Centralized Exception Handler for Django REST Framework.
    Standardizes error responses across the entire Zecpath API.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "message": "An error occurred",
            "errors": response.data,
        }

        # Status code-specific standardized messages
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_data["message"] = "Validation error"
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_data["message"] = "Authentication credentials were not provided or are invalid"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_data["message"] = "You do not have permission to perform this action"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_data["message"] = "Resource not found"
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_data["message"] = "Method not allowed"
        elif response.status_code == status.HTTP_409_CONFLICT:
            custom_data["message"] = "Conflict: Resource state conflict"

        response.data = custom_data
        return response

    # Handle unhandled 500 server errors
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return Response(
        {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error occurred. Please contact system administrator.",
            "errors": {"detail": str(exc)},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

