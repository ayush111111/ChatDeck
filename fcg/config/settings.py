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

    # Application settings
    cors_origins: list[str] = [
        "http://localhost:8000",
        "https://chat.openai.com",
        "https://chatgpt.com",
    ]
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
            "notion_api_key": "NOTION_API_KEY",
            "notion_page_id": "NOTION_PAGE_ID",
        }
