"""Tests for crawl service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.crawl_service import CrawlService
from app.models import CrawlRequest, CrawlResponse, JobStatusResponse
from app.cloudflare_client import CloudflareAPIError


@pytest.mark.asyncio
class TestCrawlService:
    """Tests for CrawlService class."""
    
    @pytest.fixture
    def service(self):
        """Create CrawlService instance."""
        return CrawlService()
    
    @pytest.fixture
    def mock_cloudflare_client(self):
        """Create mock CloudflareClient."""
        mock = MagicMock()
        mock.initiate_crawl = AsyncMock()
        mock.get_job_status = AsyncMock()
        return mock
    
    async def test_initiate_crawl_success(
        self,
        service,
        mock_cloudflare_client,
        sample_crawl_request
    ):
        """Test successful crawl initiation."""
        # Setup mock
        mock_cloudflare_client.initiate_crawl.return_value = {
            "job_id": "test-job-123",
            "status": "running"
        }
        service.cloudflare_client = mock_cloudflare_client
        
        # Create request
        request = CrawlRequest(**sample_crawl_request)
        
        # Execute
        result = await service.initiate_crawl(request)
        
        # Verify
        assert isinstance(result, CrawlResponse)
        assert result.job_id == "test-job-123"
        assert result.status == "running"
        mock_cloudflare_client.initiate_crawl.assert_called_once_with(
            url="https://example.com/",
            depth=2
        )
    
    async def test_initiate_crawl_with_custom_depth(
        self,
        service,
        mock_cloudflare_client
    ):
        """Test crawl initiation with custom depth."""
        # Setup mock
        mock_cloudflare_client.initiate_crawl.return_value = {
            "job_id": "test-job-456",
            "status": "running"
        }
        service.cloudflare_client = mock_cloudflare_client
        
        # Create request with custom depth
        request = CrawlRequest(url="https://example.com", depth=5)
        
        # Execute
        result = await service.initiate_crawl(request)
        
        # Verify
        assert result.job_id == "test-job-456"
        mock_cloudflare_client.initiate_crawl.assert_called_once_with(
            url="https://example.com/",
            depth=5
        )
    
    async def test_initiate_crawl_cloudflare_error(
        self,
        service,
        mock_cloudflare_client,
        sample_crawl_request
    ):
        """Test crawl initiation with Cloudflare API error."""
        # Setup mock to raise error
        mock_cloudflare_client.initiate_crawl.side_effect = CloudflareAPIError(
            "API error",
            status_code=401
        )
        service.cloudflare_client = mock_cloudflare_client
        
        # Create request
        request = CrawlRequest(**sample_crawl_request)
        
        # Execute and verify error is propagated
        with pytest.raises(CloudflareAPIError) as exc_info:
            await service.initiate_crawl(request)
        
        assert exc_info.value.status_code == 401
        assert "API error" in str(exc_info.value)
    
    async def test_get_crawl_status_success(
        self,
        service,
        mock_cloudflare_client
    ):
        """Test successful job status retrieval."""
        # Setup mock
        expected_response = JobStatusResponse(
            job_id="test-job-123",
            status="completed",
            total=5,
            finished=5,
            browser_seconds_used=10.5,
            results=[]
        )
        mock_cloudflare_client.get_job_status.return_value = expected_response
        service.cloudflare_client = mock_cloudflare_client
        
        # Execute
        result = await service.get_crawl_status("test-job-123")
        
        # Verify
        assert isinstance(result, JobStatusResponse)
        assert result.job_id == "test-job-123"
        assert result.status == "completed"
        assert result.total == 5
        assert result.finished == 5
        mock_cloudflare_client.get_job_status.assert_called_once_with("test-job-123")
    
    async def test_get_crawl_status_running(
        self,
        service,
        mock_cloudflare_client
    ):
        """Test job status retrieval for running job."""
        # Setup mock
        expected_response = JobStatusResponse(
            job_id="test-job-123",
            status="running",
            total=10,
            finished=3,
            browser_seconds_used=5.2,
            results=[]
        )
        mock_cloudflare_client.get_job_status.return_value = expected_response
        service.cloudflare_client = mock_cloudflare_client
        
        # Execute
        result = await service.get_crawl_status("test-job-123")
        
        # Verify
        assert result.status == "running"
        assert result.total == 10
        assert result.finished == 3
    
    async def test_get_crawl_status_not_found(
        self,
        service,
        mock_cloudflare_client
    ):
        """Test job status retrieval for non-existent job."""
        # Setup mock to raise 404 error
        mock_cloudflare_client.get_job_status.side_effect = CloudflareAPIError(
            "Job not found",
            status_code=404
        )
        service.cloudflare_client = mock_cloudflare_client
        
        # Execute and verify error is propagated
        with pytest.raises(CloudflareAPIError) as exc_info:
            await service.get_crawl_status("non-existent-job")
        
        assert exc_info.value.status_code == 404
    
    async def test_get_crawl_status_cloudflare_error(
        self,
        service,
        mock_cloudflare_client
    ):
        """Test job status retrieval with Cloudflare API error."""
        # Setup mock to raise error
        mock_cloudflare_client.get_job_status.side_effect = CloudflareAPIError(
            "API error",
            status_code=500
        )
        service.cloudflare_client = mock_cloudflare_client
        
        # Execute and verify error is propagated
        with pytest.raises(CloudflareAPIError) as exc_info:
            await service.get_crawl_status("test-job-123")
        
        assert exc_info.value.status_code == 500
    
    def test_service_initialization(self, service):
        """Test that service initializes with CloudflareClient."""
        from app.cloudflare_client import CloudflareClient
        assert isinstance(service.cloudflare_client, CloudflareClient)
    
    async def test_initiate_crawl_url_conversion(
        self,
        service,
        mock_cloudflare_client
    ):
        """Test that URL is properly converted to string."""
        # Setup mock
        mock_cloudflare_client.initiate_crawl.return_value = {
            "job_id": "test-job-789",
            "status": "running"
        }
        service.cloudflare_client = mock_cloudflare_client
        
        # Create request with HttpUrl
        request = CrawlRequest(url="https://example.com/path", depth=1)
        
        # Execute
        await service.initiate_crawl(request)
        
        # Verify URL was converted to string
        call_args = mock_cloudflare_client.initiate_crawl.call_args
        assert isinstance(call_args.kwargs["url"], str)
        assert call_args.kwargs["url"] == "https://example.com/path"

# Made with Bob
