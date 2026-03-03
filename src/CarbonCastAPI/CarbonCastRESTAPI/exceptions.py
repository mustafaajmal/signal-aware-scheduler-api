"""
Custom exception handler so API errors always return JSON instead of Django's HTML debug page.
"""
import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from .consts import carbon_cast_version
from .helper import RealTimeDataNotFoundError

logger = logging.getLogger(__name__)


def carboncast_exception_handler(exc, context):
    """
    Call DRF's default handler first; if it returns None (unhandled exception),
    return a JSON response so the client never gets the HTML debug page.
    """
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # Convert RealTimeDataNotFoundError to 404 JSON (in case it wasn't caught in view)
    if isinstance(exc, RealTimeDataNotFoundError):
        return Response(
            {"error": str(exc.message), "carbon_cast_version": carbon_cast_version},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Any other unhandled exception: return 500 with JSON (no HTML debug page)
    logger.exception("Unhandled exception in API: %s", exc)
    return Response(
        {
            "error": str(exc) or "Internal server error",
            "carbon_cast_version": carbon_cast_version,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
