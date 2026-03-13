"""Crawl service for handling crawl operations."""
import logging
from ..cloudflare_client import CloudflareClient, CloudflareAPIError
from ..models import CrawlRequest, CrawlResponse, JobStatusResponse

logger = logging.getLogger(__name__)


class CrawlService:
    """Service for managing crawl operations."""
    
    def __init__(self):
        """Initialize the crawl service."""
        self.cloudflare_client = CloudflareClient()
    
    async def initiate_crawl(self, request: CrawlRequest) -> CrawlResponse:
        """
        Initiate a new crawl job.
        
        Args:
            request: CrawlRequest containing URL and depth
            
        Returns:
            CrawlResponse with job_id and initial status
            
        Raises:
            CloudflareAPIError: If crawl initiation fails
        """
        logger.info(f"Initiating crawl for URL: {request.url}, depth: {request.depth}")
        
        result = await self.cloudflare_client.initiate_crawl(
            url=str(request.url),
            depth=request.depth
        )
        
        return CrawlResponse(
            job_id=result["job_id"],
            status=result["status"]
        )
    
    async def get_crawl_status(self, job_id: str) -> JobStatusResponse:
        """
        Get the status and results of a crawl job.
        
        Args:
            job_id: Unique identifier for the crawl job
            
        Returns:
            JobStatusResponse with current status and results
            
        Raises:
            CloudflareAPIError: If status retrieval fails
        """
        logger.info(f"Fetching status for job: {job_id}")
        return await self.cloudflare_client.get_job_status(job_id)

# Made with Bob
