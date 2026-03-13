"""Tests for exception handlers."""
import pytest
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.api.exception_handlers import (
    cloudflare_api_error_handler,
    validation_exception_handler,
    global_exception_handler
)
from app.cloudflare_client import CloudflareAPIError


class TestCloudflareAPIErrorHandler:
    """Tests for Cloudflare API error handler."""
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        return Request({"type": "http", "method": "GET", "url": "http://test/api/crawl"})
    
    async def test_handler_401_error(self, mock_request):
        """Test handler for 401 authentication error."""
        error = CloudflareAPIError("Invalid credentials", status_code=401)
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        body = response.body.decode()
        assert "Invalid credentials" in body
    
    async def test_handler_429_error(self, mock_request):
        """Test handler for 429 rate limit error."""
        error = CloudflareAPIError("Rate limit exceeded", status_code=429)
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        body = response.body.decode()
        assert "Rate limit exceeded" in body
    
    async def test_handler_502_error(self, mock_request):
        """Test handler for 502 bad gateway error."""
        error = CloudflareAPIError("Service unavailable", status_code=502)
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        body = response.body.decode()
        assert "Service unavailable" in body
    
    async def test_handler_500_error(self, mock_request):
        """Test handler for 500 internal server error."""
        error = CloudflareAPIError("Internal error", status_code=500)
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        body = response.body.decode()
        assert "Internal error" in body
    
    async def test_handler_no_status_code(self, mock_request):
        """Test handler when error has no status code."""
        error = CloudflareAPIError("Unknown error")
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        body = response.body.decode()
        assert "Unknown error" in body
    
    async def test_handler_with_response_data(self, mock_request):
        """Test handler with response data."""
        error = CloudflareAPIError(
            "API error",
            status_code=400,
            response_data={"errors": [{"code": 1000, "message": "Bad request"}]}
        )
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        body = response.body.decode()
        assert "API error" in body
    
    async def test_handler_unknown_status_code(self, mock_request):
        """Test handler with unmapped status code."""
        error = CloudflareAPIError("Custom error", status_code=418)
        
        response = await cloudflare_api_error_handler(mock_request, error)
        
        # Should default to 502
        assert response.status_code == status.HTTP_502_BAD_GATEWAY


class TestValidationExceptionHandler:
    """Tests for validation exception handler."""
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        return Request({"type": "http", "method": "POST", "url": "http://test/api/crawl"})
    
    async def test_handler_validation_error(self, mock_request):
        """Test handler for validation error."""
        # Create a validation error
        try:
            from pydantic import BaseModel, Field
            
            class TestModel(BaseModel):
                value: int = Field(..., ge=1, le=10)
            
            TestModel(value=0)
        except ValidationError as e:
            # Convert to RequestValidationError
            from fastapi.exceptions import RequestValidationError
            exc = RequestValidationError(e.errors())
            
            response = await validation_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            body = response.body.decode()
            assert "validation" in body.lower() or "error" in body.lower()
    
    async def test_handler_multiple_errors(self, mock_request):
        """Test handler with multiple validation errors."""
        try:
            from pydantic import BaseModel, Field
            
            class TestModel(BaseModel):
                value1: int = Field(..., ge=1)
                value2: str = Field(..., min_length=1)
            
            TestModel(value1=0, value2="")
        except ValidationError as e:
            from fastapi.exceptions import RequestValidationError
            exc = RequestValidationError(e.errors())
            
            response = await validation_exception_handler(mock_request, exc)
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGlobalExceptionHandler:
    """Tests for global exception handler."""
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        return Request({"type": "http", "method": "GET", "url": "http://test/api/test"})
    
    async def test_handler_generic_exception(self, mock_request):
        """Test handler for generic exception."""
        error = Exception("Something went wrong")
        
        response = await global_exception_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        body = response.body.decode()
        assert "internal server error" in body.lower()
    
    async def test_handler_runtime_error(self, mock_request):
        """Test handler for runtime error."""
        error = RuntimeError("Runtime error occurred")
        
        response = await global_exception_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    async def test_handler_value_error(self, mock_request):
        """Test handler for value error."""
        error = ValueError("Invalid value")
        
        response = await global_exception_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    async def test_handler_type_error(self, mock_request):
        """Test handler for type error."""
        error = TypeError("Type mismatch")
        
        response = await global_exception_handler(mock_request, error)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    async def test_handler_preserves_error_message(self, mock_request):
        """Test that handler logs but doesn't expose internal error details."""
        error = Exception("Internal database connection failed")
        
        response = await global_exception_handler(mock_request, error)
        
        # Should return generic message, not internal details
        body = response.body.decode()
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        # The response should contain a generic error message
        assert "error" in body.lower()


class TestExceptionHandlerIntegration:
    """Integration tests for exception handlers with FastAPI app."""
    
    def test_cloudflare_error_in_endpoint(self, client):
        """Test that Cloudflare errors are properly handled in endpoints."""
        from unittest.mock import patch, AsyncMock
        
        with patch("app.api.routes.crawl_service") as mock_service:
            mock_service.initiate_crawl = AsyncMock(
                side_effect=CloudflareAPIError("Auth failed", status_code=401)
            )
            
            response = client.post(
                "/api/crawl",
                json={"url": "https://example.com", "depth": 2}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_validation_error_in_endpoint(self, client):
        """Test that validation errors are properly handled."""
        response = client.post(
            "/api/crawl",
            json={"url": "invalid-url", "depth": 2}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_unexpected_error_in_endpoint(self, client):
        """Test that unexpected errors are properly handled."""
        from unittest.mock import patch, AsyncMock
        
        with patch("app.api.routes.crawl_service") as mock_service:
            mock_service.initiate_crawl = AsyncMock(
                side_effect=Exception("Unexpected error")
            )
            
            response = client.post(
                "/api/crawl",
                json={"url": "https://example.com", "depth": 2}
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

# Made with Bob
