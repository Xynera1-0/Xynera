from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Xynera"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM Providers
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # External Tools
    TAVILY_API_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "Xynera/1.0"

    # MCP Configuration
    MCP_SERVER_URL: str = "http://localhost:8000"
    MCP_MODE: str = "mock"  # Options: "real" or "mock"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Orchestrator Configuration
    NUM_ORCHESTRATORS: int = 2
    ORCHESTRATOR_TIMEOUT: int = 30  # seconds
    MAX_RETRIES: int = 3

    # Agent Configuration
    AGENT_TEMPERATURE: float = 0.7
    AGENT_TIMEOUT_SECONDS: int = 30
    CONFIDENCE_THRESHOLD: float = 0.6

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
