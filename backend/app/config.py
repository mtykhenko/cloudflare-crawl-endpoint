"""Configuration management using pydantic-settings."""
import logging
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Cloudflare API Configuration
    cloudflare_account_id: str
    cloudflare_api_token: str
    
    # Server Configuration
    port: int = 8000
    log_level: str = "INFO"
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def cloudflare_api_base_url(self) -> str:
        """Construct Cloudflare API base URL."""
        return f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/browser-rendering"


def setup_logging(log_level: str) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


# Global settings instance
settings = Settings()
setup_logging(settings.log_level)
