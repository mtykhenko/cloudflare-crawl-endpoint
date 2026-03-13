"""Tests for API routes."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from app.models import CrawlResponse, JobStatusResponse, CrawlResult
from app.cloudflare_client import CloudflareAPIError


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns healthy status."""
        response = client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"


class TestCrawlEndpoint:
    """Tests for crawl initiation endpoint."""
    
    @patch("app.api.routes.crawl_service")
    def test_initiate_crawl_success(
        self,
        mock_service,
        client,
        sample_crawl_request
    ):
        """Test successful crawl initiation."""
        # Setup mock
        mock_service.initiate_crawl = AsyncMock(
            return_value=CrawlResponse(
                job_id="test-job-123",
                status="running"
            )
        )
        
        # Make request
        response = client.post("/api/crawl", json=sample_crawl_request)
        
        # Verify response
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "running"
    
    def test_initiate_crawl_invalid_url(self, client):
        """Test crawl initiation with invalid URL."""
        invalid_request = {
            "url": "not-a-valid-url",
            "depth": 2
        }
        
        response = client.post("/api/crawl", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_initiate_crawl_invalid_scheme(self, client):
        """Test crawl initiation with invalid URL scheme."""
        invalid_request = {
            "url": "ftp://example.com",
            "depth": 2
        }
        
        response = client.post("/api/crawl", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "URL must use http or https scheme" in str(data)
    
    def test_initiate_crawl_depth_too_low(self, client):
        """Test crawl initiation with depth below minimum."""
        invalid_request = {
            "url": "https://example.com",
            "depth": 0
        }
        
        response = client.post("/api/crawl", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_initiate_crawl_depth_too_high(self, client):
        """Test crawl initiation with depth above maximum."""
        invalid_request = {
            "url": "https://example.com",
            "depth": 101
        }
        
        response = client.post("/api/crawl", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_initiate_crawl_missing_url(self, client):
        """Test crawl initiation without URL."""
        invalid_request = {
            "depth": 2
        }
        
        response = client.post("/api/crawl", json=invalid_request)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_initiate_crawl_default_depth(self, client, sample_crawl_request):
        """Test crawl initiation uses default depth."""
        request_without_depth = {
            "url": sample_crawl_request["url"]
        }
        
        with patch("app.api.routes.crawl_service") as mock_service:
            mock_service.initiate_crawl = AsyncMock(
                return_value=CrawlResponse(
                    job_id="test-job-456",
                    status="running"
                )
            )
            
            response = client.post("/api/crawl", json=request_without_depth)
            
            assert response.status_code == status.HTTP_202_ACCEPTED
    
    @patch("app.api.routes.crawl_service")
    def test_initiate_crawl_cloudflare_auth_error(
        self,
        mock_service,
        client,
        sample_crawl_request
    ):
        """Test crawl initiation with Cloudflare authentication error."""
        # Setup mock to raise auth error
        mock_service.initiate_crawl = AsyncMock(
            side_effect=CloudflareAPIError(
                "Authentication failed",
                status_code=401
            )
        )
        
        response = client.post("/api/crawl", json=sample_crawl_request)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Authentication failed" in data["detail"]
    
    @patch("app.api.routes.crawl_service")
    def test_initiate_crawl_cloudflare_rate_limit(
        self,
        mock_service,
        client,
        sample_crawl_request
    ):
        """Test crawl initiation with rate limit error."""
        # Setup mock to raise rate limit error
        mock_service.initiate_crawl = AsyncMock(
            side_effect=CloudflareAPIError(
                "Rate limit exceeded",
                status_code=429
            )
        )
        
        response = client.post("/api/crawl", json=sample_crawl_request)
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    @patch("app.api.routes.crawl_service")
    def test_initiate_crawl_unexpected_error(
        self,
        mock_service,
        client,
        sample_crawl_request
    ):
        """Test crawl initiation with unexpected error."""
        # Setup mock to raise unexpected error
        mock_service.initiate_crawl = AsyncMock(
            side_effect=Exception("Unexpected error")
        )
        
        response = client.post("/api/crawl", json=sample_crawl_request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestJobStatusEndpoint:
    """Tests for job status endpoint."""
    
    @patch("app.api.routes.crawl_service")
    def test_get_job_status_completed(
        self,
        mock_service,
        client
    ):
        """Test getting status of completed job."""
        job_id = "test-job-123"
        
        # Setup mock
        mock_service.get_crawl_status = AsyncMock(
            return_value=JobStatusResponse(
                job_id=job_id,
                status="completed",
                total=5,
                finished=5,
                browser_seconds_used=10.5,
                results=[
                    CrawlResult(
                        url="https://example.com",
                        status="completed",
                        markdown="# Test"
                    )
                ]
            )
        )
        
        response = client.get(f"/api/crawl/{job_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "completed"
        assert data["total"] == 5
        assert data["finished"] == 5
        assert len(data["results"]) == 1
    
    @patch("app.api.routes.crawl_service")
    def test_get_job_status_running(
        self,
        mock_service,
        client
    ):
        """Test getting status of running job."""
        job_id = "test-job-456"
        
        # Setup mock
        mock_service.get_crawl_status = AsyncMock(
            return_value=JobStatusResponse(
                job_id=job_id,
                status="running",
                total=10,
                finished=3,
                browser_seconds_used=5.2,
                results=[]
            )
        )
        
        response = client.get(f"/api/crawl/{job_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "running"
        assert data["total"] == 10
        assert data["finished"] == 3
    
    @patch("app.api.routes.crawl_service")
    def test_get_job_status_not_found(
        self,
        mock_service,
        client
    ):
        """Test getting status of non-existent job."""
        job_id = "non-existent-job"
        
        # Setup mock to raise 404 error
        mock_service.get_crawl_status = AsyncMock(
            side_effect=CloudflareAPIError(
                "Job not found",
                status_code=404
            )
        )
        
        response = client.get(f"/api/crawl/{job_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @patch("app.api.routes.crawl_service")
    def test_get_job_status_cloudflare_error(
        self,
        mock_service,
        client
    ):
        """Test getting status with Cloudflare API error."""
        job_id = "test-job-789"
        
        # Setup mock to raise API error
        mock_service.get_crawl_status = AsyncMock(
            side_effect=CloudflareAPIError(
                "API error",
                status_code=502
            )
        )
        
        response = client.get(f"/api/crawl/{job_id}")
        
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
    
    @patch("app.api.routes.crawl_service")
    def test_get_job_status_unexpected_error(
        self,
        mock_service,
        client
    ):
        """Test getting status with unexpected error."""
        job_id = "test-job-999"
        
        # Setup mock to raise unexpected error
        mock_service.get_crawl_status = AsyncMock(
            side_effect=Exception("Unexpected error")
        )
        
        response = client.get(f"/api/crawl/{job_id}")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_get_job_status_with_special_characters(self, client):
        """Test job status endpoint with special characters in job_id."""
        job_id = "test-job-with-special-chars-123"
        
        with patch("app.api.routes.crawl_service") as mock_service:
            mock_service.get_crawl_status = AsyncMock(
                return_value=JobStatusResponse(
                    job_id=job_id,
                    status="running",
                    total=0,
                    finished=0
                )
            )
            
            response = client.get(f"/api/crawl/{job_id}")
            
            assert response.status_code == status.HTTP_200_OK


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_allows_configured_origins(self, client):
        """Test that configured origins are allowed."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == status.HTTP_200_OK

# Made with Bob
