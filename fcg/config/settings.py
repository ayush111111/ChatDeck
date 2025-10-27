from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # OpenRouter API settings
    openrouter_api_key: str
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_model: str = "qwen/qwen3-4b:free"
    openrouter_max_tokens: int

    # Notion API settings
    notion_api_key: Optional[str] = None
    notion_page_id: Optional[str] = None

    # Database settings - Auto-detects PostgreSQL vs SQLite
    postgres_enabled: bool = False  # Set to true to use PostgreSQL
    database_url: str = "sqlite:///data/flashcards.db"  # Default: local SQLite

    # PostgreSQL settings (when postgres_enabled=true)
    postgres_host: Optional[str] = None  # Database host
    postgres_user: Optional[str] = None  # Database user
    postgres_password: Optional[str] = None  # Database password
    postgres_db: Optional[str] = None  # Database name
    postgres_port: int = 5432  # Default PostgreSQL port

    # Celery settings (for future use)
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    use_celery: bool = False  # Fallback flag

    # Application settings
    cors_origins: list[str] = ["http://localhost:8000", "https://chat.openai.com", "https://chatgpt.com", "*"]
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False

        # Map environment variables to settings
        env_field_names = {
            "openrouter_api_key": "OPENROUTER_API_KEY",
            "openrouter_url": "OPENROUTER_URL",
            "openrouter_model": "OPENROUTER_MODEL",
            "openrouter_max_tokens": "OPENROUTER_MAX_TOKENS",
            "notion_api_key": "NOTION_API_KEY",
            "notion_page_id": "NOTION_PAGE_ID",
            "postgres_enabled": "POSTGRES_ENABLED",
            "database_url": "DATABASE_URL",
            "postgres_host": "POSTGRES_HOST",
            "postgres_user": "POSTGRES_USER",
            "postgres_password": "POSTGRES_PASSWORD",
            "postgres_db": "POSTGRES_DB",
            "postgres_port": "POSTGRES_PORT",
            "celery_broker_url": "CELERY_BROKER_URL",
            "celery_result_backend": "CELERY_RESULT_BACKEND",
            "use_celery": "USE_CELERY",
        }
