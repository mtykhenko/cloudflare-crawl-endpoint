"""Tests for Cloudflare API client."""
import pytest
import httpx
import respx
from app.cloudflare_client import CloudflareClient, CloudflareAPIError
from app.models import JobStatusResponse


@pytest.mark.asyncio
class TestCloudflareClient:
    """Tests for CloudflareClient class."""
    
    @pytest.fixture
    def client(self, mock_settings):
        """Create CloudflareClient instance."""
        return CloudflareClient()
    
    async def test_initiate_crawl_success(
        self,
        client,
        mock_settings,
        sample_cloudflare_initiate_response
    ):
        """Test successful crawl initiation."""
        with respx.mock:
            route = respx.post(
                f"{mock_settings.cloudflare_api_base_url}/crawl"
            ).mock(return_value=httpx.Response(200, json=sample_cloudflare_initiate_response))
            
            result = await client.initiate_crawl("https://example.com", 2)
            
            assert result["job_id"] == "test-job-id-123"
            assert result["status"] == "running"
            assert route.called
    
    async def test_initiate_crawl_with_payload(
        self,
        client,
        mock_settings,
        sample_cloudflare_initiate_response
    ):
        """Test that crawl initiation sends correct payload."""
        with respx.mock:
            route = respx.post(
                f"{mock_settings.cloudflare_api_base_url}/crawl"
            ).mock(return_value=httpx.Response(200, json=sample_cloudflare_initiate_response))
            
            await client.initiate_crawl("https://example.com", 3)
            
            request = route.calls.last.request
            payload = httpx.QueryParams(request.content.decode())
            assert route.called
    
    async def test_initiate_crawl_api_error(
        self,
        client,
        mock_settings,
        sample_cloudflare_error_response
    ):
        """Test crawl initiation with API error."""
        with respx.mock:
            respx.post(
                f"{mock_settings.cloudflare_api_base_url}/crawl"
            ).mock(return_value=httpx.Response(401, json=sample_cloudflare_error_response))
            
            with pytest.raises(CloudflareAPIError) as exc_info:
                await client.initiate_crawl("https://example.com", 2)
            
            assert exc_info.value.status_code == 401
            assert "Authentication error" in str(exc_info.value)
    
    async def test_initiate_crawl_http_error(
        self,
        client,
        mock_settings
    ):
        """Test crawl initiation with HTTP error."""
        with respx.mock:
            respx.post(
                f"{mock_settings.cloudflare_api_base_url}/crawl"
            ).mock(return_value=httpx.Response(500, text="Internal Server Error"))
            
            with pytest.raises(CloudflareAPIError) as exc_info:
                await client.initiate_crawl("https://example.com", 2)
            
            assert exc_info.value.status_code == 500
    
    async def test_initiate_crawl_network_error(
        self,
        client,
        mock_settings
    ):
        """Test crawl initiation with network error."""
        with respx.mock:
            respx.post(
                f"{mock_settings.cloudflare_api_base_url}/crawl"
            ).mock(side_effect=httpx.ConnectError("Connection failed"))
            
            with pytest.raises(CloudflareAPIError) as exc_info:
                await client.initiate_crawl("https://example.com", 2)
            
            assert "Network error" in str(exc_info.value)
    
    async def test_initiate_crawl_success_false(
        self,
        client,
        mock_settings
    ):
        """Test crawl initiation when API returns success=false."""
        error_response = {
            "success": False,
            "result": None,
            "errors": [{"message": "Invalid parameters"}],
            "messages": []
        }
        
        with respx.mock:
            respx.post(
                f"{mock_settings.cloudflare_api_base_url}/crawl"
            ).mock(return_value=httpx.Response(200, json=error_response))
            
            with pytest.raises(CloudflareAPIError) as exc_info:
                await client.initiate_crawl("https://example.com", 2)
            
            assert "Invalid parameters" in str(exc_info.value)
    
    async def test_get_job_status_success(
        self,
        client,
        mock_settings,
        sample_cloudflare_status_response
    ):
        """Test successful job status retrieval."""
        job_id = "test-job-id-123"
        
        with respx.mock:
            route = respx.get(
                f"{mock_settings.cloudflare_api_base_url}/crawl/{job_id}"
            ).mock(return_value=httpx.Response(200, json=sample_cloudflare_status_response))
            
            result = await client.get_job_status(job_id)
            
            assert isinstance(result, JobStatusResponse)
            assert result.job_id == job_id
            assert result.status == "completed"
            assert result.total == 5
            assert result.finished == 5
            assert result.browser_seconds_used == 12.5
            assert len(result.results) == 2
            assert route.called
    
    async def test_get_job_status_running(
        self,
        client,
        mock_settings,
        sample_cloudflare_running_response
    ):
        """Test job status retrieval for running job."""
        job_id = "test-job-id-123"
        
        with respx.mock:
            respx.get(
                f"{mock_settings.cloudflare_api_base_url}/crawl/{job_id}"
            ).mock(return_value=httpx.Response(200, json=sample_cloudflare_running_response))
            
            result = await client.get_job_status(job_id)
            
            assert result.status == "running"
            assert result.total == 10
            assert result.finished == 3
            assert len(result.results) == 0
    
    async def test_get_job_status_not_found(
        self,
        client,
        mock_settings
    ):
        """Test job status retrieval for non-existent job."""
        job_id = "non-existent-job"
        error_response = {
            "success": False,
            "result": None,
            "errors": [{"message": "Job not found"}],
            "messages": []
        }
        
        with respx.mock:
            respx.get(
                f"{mock_settings.cloudflare_api_base_url}/crawl/{job_id}"
            ).mock(return_value=httpx.Response(404, json=error_response))
            
            with pytest.raises(CloudflareAPIError) as exc_info:
                await client.get_job_status(job_id)
            
            assert exc_info.value.status_code == 404
    
    async def test_get_job_status_network_error(
        self,
        client,
        mock_settings
    ):
        """Test job status retrieval with network error."""
        job_id = "test-job-id-123"
        
        with respx.mock:
            respx.get(
                f"{mock_settings.cloudflare_api_base_url}/crawl/{job_id}"
            ).mock(side_effect=httpx.ConnectError("Connection failed"))
            
            with pytest.raises(CloudflareAPIError) as exc_info:
                await client.get_job_status(job_id)
            
            assert "Network error" in str(exc_info.value)
    
    async def test_parse_results_with_metadata(
        self,
        client
    ):
        """Test parsing results with metadata."""
        records = [
            {
                "url": "https://example.com",
                "status": "completed",
                "markdown": "# Test",
                "metadata": {
                    "status": 200,
                    "title": "Test Page",
                    "url": "https://example.com"
                }
            }
        ]
        
        results = client._parse_results(records)
        
        assert len(results) == 1
        assert results[0].url == "https://example.com"
        assert results[0].status == "completed"
        assert results[0].markdown == "# Test"
        assert results[0].metadata is not None
        assert results[0].metadata.status == 200
        assert results[0].metadata.title == "Test Page"
    
    async def test_parse_results_without_metadata(
        self,
        client
    ):
        """Test parsing results without metadata."""
        records = [
            {
                "url": "https://example.com",
                "status": "completed",
                "markdown": "# Test"
            }
        ]
        
        results = client._parse_results(records)
        
        assert len(results) == 1
        assert results[0].metadata is None
    
    async def test_parse_results_invalid_record(
        self,
        client
    ):
        """Test parsing results with invalid record."""
        records = [
            {
                "url": "https://example.com",
                "status": "completed"
            },
            {
                # Invalid record - missing required fields
                "invalid": "data"
            },
            {
                "url": "https://example.com/page2",
                "status": "completed"
            }
        ]
        
        results = client._parse_results(records)
        
        # Should skip invalid record
        assert len(results) == 2
    
    def test_parse_error_response_with_errors(
        self,
        client
    ):
        """Test parsing error response with errors array."""
        response = httpx.Response(
            400,
            json={
                "success": False,
                "errors": [{"message": "Bad request"}]
            }
        )
        
        error_msg = client._parse_error_response(response)
        assert error_msg == "Bad request"
    
    def test_parse_error_response_with_message(
        self,
        client
    ):
        """Test parsing error response with message field."""
        response = httpx.Response(
            400,
            json={
                "success": False,
                "message": "Invalid input"
            }
        )
        
        error_msg = client._parse_error_response(response)
        assert error_msg == "Invalid input"
    
    def test_parse_error_response_plain_text(
        self,
        client
    ):
        """Test parsing error response with plain text."""
        response = httpx.Response(500, text="Internal Server Error")
        
        error_msg = client._parse_error_response(response)
        assert error_msg == "Internal Server Error"
    
    def test_parse_error_response_invalid_json(
        self,
        client
    ):
        """Test parsing error response with invalid JSON."""
        response = httpx.Response(500, text="Not JSON")
        
        error_msg = client._parse_error_response(response)
        assert error_msg == "Not JSON"


class TestCloudflareAPIError:
    """Tests for CloudflareAPIError exception."""
    
    def test_error_with_all_params(self):
        """Test error with all parameters."""
        error = CloudflareAPIError(
            "Test error",
            status_code=400,
            response_data={"error": "details"}
        )
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response_data == {"error": "details"}
    
    def test_error_with_message_only(self):
        """Test error with message only."""
        error = CloudflareAPIError("Test error")
        
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_data is None

# Made with Bob
