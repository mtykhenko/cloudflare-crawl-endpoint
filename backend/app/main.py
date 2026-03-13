"""FastAPI application for web crawler backend."""
import logging
from contextlib import asynccontextmanager
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import router
from .api.exception_handlers import (
    cloudflare_api_error_handler,
    validation_exception_handler,
    global_exception_handler,
)
from .cloudflare_client import CloudflareAPIError


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Web Crawler API")
    logger.info(f"CORS origins: {settings.cors_origins_list}")
    yield
    logger.info("Shutting down Web Crawler API")


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers for the application.
    
    This centralizes exception handling configuration and makes it easier
    to add new handlers without modifying the main application setup.
    All handlers are registered using the same pattern for consistency.
    
    Handler implementations are in api/exception_handlers.py for better
    separation of concerns and easier testing.
    
    Args:
        app: The FastAPI application instance
    """
    # Register all exception handlers using consistent pattern
    exception_handlers: list[tuple[type[Exception], Callable[..., Any]]] = [
        (CloudflareAPIError, cloudflare_api_error_handler),
        (RequestValidationError, validation_exception_handler),
        (Exception, global_exception_handler),
    ]
    
    for exc_class, handler in exception_handlers:
        app.add_exception_handler(exc_class, handler)  # type: ignore[arg-type]
        logger.debug(f"Registered exception handler for {exc_class.__name__}")
    
    logger.info(f"Successfully registered {len(exception_handlers)} exception handlers")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Web Crawler API",
        description="API for crawling websites using Cloudflare Browser Rendering",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
