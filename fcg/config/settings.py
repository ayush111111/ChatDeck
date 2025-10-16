from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # OpenRouter API settings
    openrouter_api_key: str
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_model: str = "qwen/qwen3-4b:free"

    # Notion API settings
    notion_api_key: Optional[str] = None
    notion_page_id: Optional[str] = None

    # Database settings
    database_url: str = "sqlite:///./flashcards.db"
    
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
            "notion_api_key": "NOTION_API_KEY",
            "notion_page_id": "NOTION_PAGE_ID",
            "database_url": "DATABASE_URL",
            "celery_broker_url": "CELERY_BROKER_URL",
            "celery_result_backend": "CELERY_RESULT_BACKEND",
            "use_celery": "USE_CELERY",
        }
