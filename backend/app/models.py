"""Pydantic models for request/response validation."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


class CrawlRequest(BaseModel):
    """Request model for initiating a crawl."""
    
    url: HttpUrl = Field(..., description="The URL to start crawling from")
    depth: int = Field(
        default=2,
        ge=1,
        le=100,
        description="Maximum link depth to crawl (1-100)"
    )
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL has a valid scheme."""
        if v.scheme not in ['http', 'https']:
            raise ValueError('URL must use http or https scheme')
        return v


class CrawlResponse(BaseModel):
    """Response model for crawl initiation."""
    
    job_id: str = Field(..., description="Unique identifier for the crawl job")
    status: str = Field(..., description="Current status of the crawl job")


class CrawlResultMetadata(BaseModel):
    """Metadata for a single crawled page."""
    
    status: int = Field(..., description="HTTP status code")
    title: Optional[str] = Field(None, description="Page title")
    url: str = Field(..., description="Page URL")


class CrawlResult(BaseModel):
    """Result for a single crawled page."""
    
    url: str = Field(..., description="Page URL")
    status: Literal["completed", "queued", "disallowed", "skipped", "errored", "cancelled"] = Field(
        ..., 
        description="Status of this specific page crawl"
    )
    markdown: Optional[str] = Field(None, description="Page content in Markdown format")
    metadata: Optional[CrawlResultMetadata] = Field(None, description="Page metadata")


class JobStatusResponse(BaseModel):
    """Response model for job status query."""
    
    job_id: str = Field(..., description="Unique identifier for the crawl job")
    status: Literal["running", "completed", "cancelled_by_user", "cancelled_due_to_timeout", "cancelled_due_to_limits", "errored"] = Field(
        ...,
        description="Current status of the crawl job"
    )
    total: int = Field(default=0, description="Total number of pages discovered")
    finished: int = Field(default=0, description="Number of pages finished processing")
    browser_seconds_used: Optional[float] = Field(None, description="Browser time consumed in seconds")
    results: List[CrawlResult] = Field(default_factory=list, description="List of crawled pages")
    cursor: Optional[int] = Field(None, description="Pagination cursor for large result sets")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(default="healthy", description="Service health status")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")
