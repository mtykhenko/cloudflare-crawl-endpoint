"""Cloudflare Browser Rendering API client."""
import logging
from typing import Dict, Any, Optional
import httpx
from .config import settings
from .models import JobStatusResponse, CrawlResult, CrawlResultMetadata


logger = logging.getLogger(__name__)


class CloudflareAPIError(Exception):
    """Custom exception for Cloudflare API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class CloudflareClient:
    """Client for interacting with Cloudflare Browser Rendering API."""
    
    def __init__(self):
        """Initialize the Cloudflare API client."""
        self.base_url = settings.cloudflare_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.cloudflare_api_token}",
            "Content-Type": "application/json"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
    async def initiate_crawl(self, url: str, depth: int) -> Dict[str, Any]:
        """
        Initiate a crawl job with Cloudflare.
        
        Args:
            url: The starting URL to crawl
            depth: Maximum link depth to crawl
            
        Returns:
            Dict containing job_id and initial status
            
        Raises:
            CloudflareAPIError: If the API request fails
        """
        endpoint = f"{self.base_url}/crawl"
        
        payload = {
            "url": str(url),
            "depth": depth,
            "formats": ["markdown"],
            "render": True,
            "limit": 100  # Reasonable limit for initial implementation
        }
        
        logger.info(f"Initiating crawl for URL: {url} with depth: {depth}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success"):
                    error_msg = data.get("errors", [{}])[0].get("message", "Unknown error")
                    logger.error(f"Cloudflare API returned success=false: {error_msg}")
                    raise CloudflareAPIError(
                        f"Failed to initiate crawl: {error_msg}",
                        status_code=response.status_code,
                        response_data=data
                    )
                
                job_id = data.get("result")
                logger.info(f"Crawl initiated successfully. Job ID: {job_id}")
                
                return {
                    "job_id": job_id,
                    "status": "running"
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during crawl initiation: {e.response.status_code} - {e.response.text}")
            error_detail = self._parse_error_response(e.response)
            raise CloudflareAPIError(
                f"HTTP {e.response.status_code}: {error_detail}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Request error during crawl initiation: {str(e)}")
            raise CloudflareAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during crawl initiation: {str(e)}")
            raise CloudflareAPIError(f"Unexpected error: {str(e)}")
    
    async def get_job_status(self, job_id: str) -> JobStatusResponse:
        """
        Get the status and results of a crawl job.
        
        Args:
            job_id: The unique identifier for the crawl job
            
        Returns:
            JobStatusResponse containing job status and results
            
        Raises:
            CloudflareAPIError: If the API request fails
        """
        endpoint = f"{self.base_url}/crawl/{job_id}"
        
        logger.info(f"Fetching status for job: {job_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success"):
                    error_msg = data.get("errors", [{}])[0].get("message", "Unknown error")
                    logger.error(f"Cloudflare API returned success=false: {error_msg}")
                    raise CloudflareAPIError(
                        f"Failed to get job status: {error_msg}",
                        status_code=response.status_code,
                        response_data=data
                    )
                
                result = data.get("result", {})
                
                # Transform Cloudflare response to our model
                job_status = JobStatusResponse(
                    job_id=result.get("id", job_id),
                    status=result.get("status", "unknown"),
                    total=result.get("total", 0),
                    finished=result.get("finished", 0),
                    browser_seconds_used=result.get("browserSecondsUsed"),
                    results=self._parse_results(result.get("records", [])),
                    cursor=result.get("cursor")
                )
                
                logger.info(f"Job {job_id} status: {job_status.status}, finished: {job_status.finished}/{job_status.total}")
                
                return job_status
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching job status: {e.response.status_code} - {e.response.text}")
            error_detail = self._parse_error_response(e.response)
            raise CloudflareAPIError(
                f"HTTP {e.response.status_code}: {error_detail}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Request error fetching job status: {str(e)}")
            raise CloudflareAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching job status: {str(e)}")
            raise CloudflareAPIError(f"Unexpected error: {str(e)}")
    
    def _parse_results(self, records: list) -> list[CrawlResult]:
        """
        Parse Cloudflare crawl records into CrawlResult objects.
        
        Args:
            records: List of record dictionaries from Cloudflare API
            
        Returns:
            List of CrawlResult objects
        """
        results = []
        
        for record in records:
            try:
                metadata = None
                if record.get("metadata"):
                    metadata = CrawlResultMetadata(
                        status=record["metadata"].get("status", 0),
                        title=record["metadata"].get("title"),
                        url=record["metadata"].get("url", record.get("url", ""))
                    )
                
                result = CrawlResult(
                    url=record.get("url", ""),
                    status=record.get("status", "unknown"),
                    markdown=record.get("markdown"),
                    metadata=metadata
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse record: {e}")
                continue
        
        return results
    
    def _parse_error_response(self, response: httpx.Response) -> str:
        """
        Parse error details from Cloudflare API response.
        
        Args:
            response: The HTTP response object
            
        Returns:
            Error message string
        """
        try:
            data = response.json()
            if errors := data.get("errors"):
                return errors[0].get("message", "Unknown error")
            return data.get("message", response.text)
        except Exception:
            return response.text or "Unknown error"
