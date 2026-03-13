"""API routes for crawl operations."""
import logging
from fastapi import APIRouter, HTTPException, status
from ..models import (
    CrawlRequest,
    CrawlResponse,
    JobStatusResponse,
    HealthResponse,
    ErrorResponse
)
from ..services.crawl_service import CrawlService
from ..cloudflare_client import CloudflareAPIError

logger = logging.getLogger(__name__)
router = APIRouter()
crawl_service = CrawlService()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse indicating service is healthy
    """
    return HealthResponse(status="healthy")


@router.post(
    "/crawl",
    response_model=CrawlResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Crawl"],
    responses={
        202: {"description": "Crawl job initiated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        401: {"model": ErrorResponse, "description": "Invalid Cloudflare credentials"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "Cloudflare API error"}
    }
)
async def initiate_crawl(request: CrawlRequest):
    """
    Initiate a new crawl job.
    
    Args:
        request: CrawlRequest containing URL and depth
        
    Returns:
        CrawlResponse with job_id and initial status
        
    Raises:
        HTTPException: If crawl initiation fails
    """
    try:
        return await crawl_service.initiate_crawl(request)
    except CloudflareAPIError:
        # Re-raise to be handled by exception handler
        raise
    except Exception as e:
        logger.error(f"Unexpected error initiating crawl: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate crawl: {str(e)}"
        )


@router.get(
    "/crawl/{job_id}",
    response_model=JobStatusResponse,
    tags=["Crawl"],
    responses={
        200: {"description": "Job status retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Job not found"},
        401: {"model": ErrorResponse, "description": "Invalid Cloudflare credentials"},
        502: {"model": ErrorResponse, "description": "Cloudflare API error"}
    }
)
async def get_crawl_status(job_id: str):
    """
    Get the status and results of a crawl job.
    
    Args:
        job_id: Unique identifier for the crawl job
        
    Returns:
        JobStatusResponse with current status and results
        
    Raises:
        HTTPException: If status retrieval fails
    """
    try:
        return await crawl_service.get_crawl_status(job_id)
    except CloudflareAPIError as e:
        # Check if it's a 404 (job not found)
        if e.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crawl job not found: {job_id}"
            )
        # Re-raise other Cloudflare errors to be handled by exception handler
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting job status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )

# Made with Bob
