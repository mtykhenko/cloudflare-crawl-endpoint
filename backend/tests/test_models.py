"""Tests for Pydantic models."""
import pytest
from pydantic import ValidationError
from app.models import (
    CrawlRequest,
    CrawlResponse,
    CrawlResult,
    CrawlResultMetadata,
    JobStatusResponse,
    HealthResponse,
    ErrorResponse
)


class TestCrawlRequest:
    """Tests for CrawlRequest model."""
    
    def test_valid_request(self):
        """Test valid crawl request."""
        request = CrawlRequest(url="https://example.com", depth=2)
        assert str(request.url) == "https://example.com/"
        assert request.depth == 2
    
    def test_default_depth(self):
        """Test default depth value."""
        request = CrawlRequest(url="https://example.com")
        assert request.depth == 2
    
    def test_http_url_allowed(self):
        """Test that HTTP URLs are allowed."""
        request = CrawlRequest(url="http://example.com", depth=1)
        assert str(request.url) == "http://example.com/"
    
    def test_invalid_scheme(self):
        """Test that invalid URL schemes are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CrawlRequest(url="ftp://example.com", depth=2)
        assert "URL must use http or https scheme" in str(exc_info.value)
    
    def test_depth_too_low(self):
        """Test that depth below 1 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CrawlRequest(url="https://example.com", depth=0)
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_depth_too_high(self):
        """Test that depth above 100 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CrawlRequest(url="https://example.com", depth=101)
        assert "less than or equal to 100" in str(exc_info.value)
    
    def test_invalid_url(self):
        """Test that invalid URLs are rejected."""
        with pytest.raises(ValidationError):
            CrawlRequest(url="not-a-url", depth=2)
    
    def test_missing_url(self):
        """Test that missing URL is rejected."""
        with pytest.raises(ValidationError):
            CrawlRequest(depth=2)


class TestCrawlResponse:
    """Tests for CrawlResponse model."""
    
    def test_valid_response(self):
        """Test valid crawl response."""
        response = CrawlResponse(job_id="test-123", status="running")
        assert response.job_id == "test-123"
        assert response.status == "running"
    
    def test_missing_fields(self):
        """Test that missing fields are rejected."""
        with pytest.raises(ValidationError):
            CrawlResponse(job_id="test-123")


class TestCrawlResultMetadata:
    """Tests for CrawlResultMetadata model."""
    
    def test_valid_metadata(self):
        """Test valid metadata."""
        metadata = CrawlResultMetadata(
            status=200,
            title="Example",
            url="https://example.com"
        )
        assert metadata.status == 200
        assert metadata.title == "Example"
        assert metadata.url == "https://example.com"
    
    def test_optional_title(self):
        """Test that title is optional."""
        metadata = CrawlResultMetadata(
            status=200,
            url="https://example.com"
        )
        assert metadata.title is None


class TestCrawlResult:
    """Tests for CrawlResult model."""
    
    def test_valid_result(self):
        """Test valid crawl result."""
        result = CrawlResult(
            url="https://example.com",
            status="completed",
            markdown="# Test",
            metadata=CrawlResultMetadata(
                status=200,
                title="Test",
                url="https://example.com"
            )
        )
        assert result.url == "https://example.com"
        assert result.status == "completed"
        assert result.markdown == "# Test"
        assert result.metadata.status == 200
    
    def test_optional_fields(self):
        """Test that markdown and metadata are optional."""
        result = CrawlResult(
            url="https://example.com",
            status="queued"
        )
        assert result.markdown is None
        assert result.metadata is None
    
    def test_invalid_status(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            CrawlResult(
                url="https://example.com",
                status="invalid_status"
            )
    
    def test_all_valid_statuses(self):
        """Test all valid status values."""
        valid_statuses = ["completed", "queued", "disallowed", "skipped", "errored", "cancelled"]
        for status in valid_statuses:
            result = CrawlResult(url="https://example.com", status=status)
            assert result.status == status


class TestJobStatusResponse:
    """Tests for JobStatusResponse model."""
    
    def test_valid_response(self):
        """Test valid job status response."""
        response = JobStatusResponse(
            job_id="test-123",
            status="completed",
            total=10,
            finished=10,
            browser_seconds_used=15.5,
            results=[
                CrawlResult(url="https://example.com", status="completed")
            ],
            cursor=None
        )
        assert response.job_id == "test-123"
        assert response.status == "completed"
        assert response.total == 10
        assert response.finished == 10
        assert response.browser_seconds_used == 15.5
        assert len(response.results) == 1
    
    def test_default_values(self):
        """Test default values."""
        response = JobStatusResponse(
            job_id="test-123",
            status="running"
        )
        assert response.total == 0
        assert response.finished == 0
        assert response.browser_seconds_used is None
        assert response.results == []
        assert response.cursor is None
    
    def test_invalid_status(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            JobStatusResponse(
                job_id="test-123",
                status="invalid_status"
            )
    
    def test_all_valid_statuses(self):
        """Test all valid status values."""
        valid_statuses = [
            "running", "completed", "cancelled_by_user",
            "cancelled_due_to_timeout", "cancelled_due_to_limits", "errored"
        ]
        for status in valid_statuses:
            response = JobStatusResponse(job_id="test-123", status=status)
            assert response.status == status


class TestHealthResponse:
    """Tests for HealthResponse model."""
    
    def test_default_status(self):
        """Test default status value."""
        response = HealthResponse()
        assert response.status == "healthy"
    
    def test_custom_status(self):
        """Test custom status value."""
        response = HealthResponse(status="degraded")
        assert response.status == "degraded"


class TestErrorResponse:
    """Tests for ErrorResponse model."""
    
    def test_valid_error(self):
        """Test valid error response."""
        error = ErrorResponse(
            detail="Something went wrong",
            error_code="ERR_001"
        )
        assert error.detail == "Something went wrong"
        assert error.error_code == "ERR_001"
    
    def test_optional_error_code(self):
        """Test that error_code is optional."""
        error = ErrorResponse(detail="Something went wrong")
        assert error.detail == "Something went wrong"
        assert error.error_code is None

# Made with Bob
