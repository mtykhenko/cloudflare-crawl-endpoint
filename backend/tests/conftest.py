"""Pytest configuration and shared fixtures."""
import pytest
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import create_app
from app.config import Settings


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    test_settings = Settings(
        cloudflare_account_id="test_account_id",
        cloudflare_api_token="test_token",
        cors_origins="http://localhost:3000,http://localhost:5173",
        port=8000,
        log_level="INFO"
    )
    
    # Patch the settings module
    monkeypatch.setattr("app.config.settings", test_settings)
    monkeypatch.setattr("app.main.settings", test_settings)
    monkeypatch.setattr("app.cloudflare_client.settings", test_settings)
    
    return test_settings


@pytest.fixture
def app(mock_settings):
    """Create FastAPI application for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_crawl_request():
    """Sample crawl request data."""
    return {
        "url": "https://example.com",
        "depth": 2
    }


@pytest.fixture
def sample_cloudflare_initiate_response():
    """Sample Cloudflare API response for crawl initiation."""
    return {
        "success": True,
        "result": "test-job-id-123",
        "errors": [],
        "messages": []
    }


@pytest.fixture
def sample_cloudflare_status_response():
    """Sample Cloudflare API response for job status."""
    return {
        "success": True,
        "result": {
            "id": "test-job-id-123",
            "status": "completed",
            "total": 5,
            "finished": 5,
            "browserSecondsUsed": 12.5,
            "records": [
                {
                    "url": "https://example.com",
                    "status": "completed",
                    "markdown": "# Example Page\n\nThis is example content.",
                    "metadata": {
                        "status": 200,
                        "title": "Example Domain",
                        "url": "https://example.com"
                    }
                },
                {
                    "url": "https://example.com/about",
                    "status": "completed",
                    "markdown": "# About Us\n\nAbout page content.",
                    "metadata": {
                        "status": 200,
                        "title": "About - Example",
                        "url": "https://example.com/about"
                    }
                }
            ],
            "cursor": None
        },
        "errors": [],
        "messages": []
    }


@pytest.fixture
def sample_cloudflare_running_response():
    """Sample Cloudflare API response for running job."""
    return {
        "success": True,
        "result": {
            "id": "test-job-id-123",
            "status": "running",
            "total": 10,
            "finished": 3,
            "browserSecondsUsed": 5.2,
            "records": [],
            "cursor": None
        },
        "errors": [],
        "messages": []
    }


@pytest.fixture
def sample_cloudflare_error_response():
    """Sample Cloudflare API error response."""
    return {
        "success": False,
        "result": None,
        "errors": [
            {
                "code": 10000,
                "message": "Authentication error"
            }
        ],
        "messages": []
    }

# Made with Bob
