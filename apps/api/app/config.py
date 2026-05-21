"""
Application configuration loaded from environment variables.
All secrets are injected via environment; never hardcoded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database (Neon PostgreSQL)
    DATABASE_URL: str  # postgres://... or postgresql://...

    # Neon Auth — paste the JWKS URL from the Auth project info page
    # (Auth URL + /.well-known/jwks.json)
    NEON_AUTH_JWKS_URL: str

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str

    # Inngest
    INNGEST_SIGNING_KEY: str = ""
    INNGEST_EVENT_KEY: str = ""

    # OpenRouter (LLM)
    OPENROUTER_API_KEY: str

    # Tools
    TAVILY_API_KEY: str = ""

    # Vercel Blob
    VERCEL_BLOB_READ_WRITE_TOKEN: str = ""

    # CORS / Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Security
    SECRET_KEY: str = "change-this-in-production-minimum-32-chars"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # LLM defaults
    DEFAULT_MODEL: str = "openai/gpt-4o-mini"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    @property
    def async_database_url(self) -> str:
        """Convert postgres:// URL to asyncpg-compatible format."""
        url = self.DATABASE_URL
        url = url.replace("postgresql://", "postgresql+asyncpg://")
        url = url.replace("postgres://", "postgresql+asyncpg://")
        # asyncpg uses ssl=require, not sslmode=require
        if "sslmode=require" in url:
            url = url.replace("sslmode=require", "ssl=require")
        elif "?" not in url and "neon.tech" in url:
            url += "?ssl=require"
        return url

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
