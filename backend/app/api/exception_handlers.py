"""Exception handlers for the API."""
import logging
from typing import Dict, Any
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ..cloudflare_client import CloudflareAPIError
from ..config import settings


logger = logging.getLogger(__name__)


async def cloudflare_api_error_handler(request: Request, exc: CloudflareAPIError) -> JSONResponse:
    """
    Handle Cloudflare API errors with proper status code mapping and logging.
    
    This handler:
    - Maps Cloudflare-specific errors to appropriate HTTP status codes
    - Logs errors for monitoring and debugging
    - Provides consistent error response format
    - Includes retry hints for rate limiting
    
    Args:
        request: The incoming request
        exc: The CloudflareAPIError exception
        
    Returns:
        JSONResponse with appropriate status code and error details
    """
    original_status = exc.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Map Cloudflare errors to appropriate HTTP status codes
    status_code_mapping = {
        401: status.HTTP_401_UNAUTHORIZED,
        403: status.HTTP_403_FORBIDDEN,
        429: status.HTTP_429_TOO_MANY_REQUESTS,
    }
    
    # Determine final status code
    if original_status in status_code_mapping:
        mapped_status = status_code_mapping[original_status]
    elif original_status >= 500:
        mapped_status = status.HTTP_502_BAD_GATEWAY
    else:
        mapped_status = original_status
    
    # Log the error with appropriate level
    log_message = (
        f"Cloudflare API error on {request.method} {request.url.path}: "
        f"Status {original_status} -> {mapped_status}, Message: {exc.message}"
    )
    
    if mapped_status >= 500:
        logger.error(log_message, exc_info=True)
    elif mapped_status == status.HTTP_429_TOO_MANY_REQUESTS:
        logger.warning(f"{log_message} (Rate limit exceeded)")
    else:
        logger.warning(log_message)
    
    # Build response content
    content: Dict[str, Any] = {
        "detail": exc.message,
        "error_code": "CLOUDFLARE_API_ERROR"
    }
    
    # Add retry hint for rate limiting
    if mapped_status == status.HTTP_429_TOO_MANY_REQUESTS:
        content["retry_after"] = 60  # Suggest retry after 60 seconds
        content["message"] = "Rate limit exceeded. Please try again later."
    
    # Add additional context for debugging (if available)
    if exc.response_data and logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Cloudflare response data: {exc.response_data}")
    
    return JSONResponse(
        status_code=mapped_status,
        content=content
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors with detailed error messages.
    
    This handler:
    - Returns all validation errors in a single response
    - Includes field-level error information
    - Helps clients fix multiple issues at once
    
    Args:
        request: The incoming request
        exc: The validation error exception
        
    Returns:
        JSONResponse with validation error details
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed"
        }
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions to prevent information leakage.
    
    This handler:
    - Catches all unexpected exceptions
    - Prevents application crashes
    - Logs full stack traces for debugging
    - Returns safe, generic errors to clients in production
    - Shows detailed errors only in DEBUG mode
    
    Args:
        request: The incoming request
        exc: The unhandled exception
        
    Returns:
        JSONResponse with generic error message
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {str(exc)}",
        exc_info=True
    )
    
    # Don't expose internal error details in production
    error_detail = "An internal server error occurred"
    if settings.log_level.upper() == "DEBUG":
        error_detail = f"{type(exc).__name__}: {str(exc)}"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": error_detail,
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

# Made with Bob
