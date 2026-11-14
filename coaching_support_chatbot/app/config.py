"""
Application configuration using Pydantic Settings.
All sensitive values are loaded from environment variables.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "sqlite:///./chatbot_dev.db"

    # Security
    secret_key: str = "change-this-to-a-long-random-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS
    frontend_origin: str = "http://localhost:5173"

    # Optional LLM support (OpenAI, Gemini, Groq)
    openai_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "auto"

    # Rate limiting (requests per minute per IP)
    chat_rate_limit: int = 30
    form_rate_limit: int = 10
    login_rate_limit: int = 5

    # App metadata
    app_name: str = "Future Vision Classes – AI Support Chatbot"
    app_version: str = "1.0.0"
    debug: bool = False

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_llm(self) -> bool:
        return bool(self.openai_api_key or self.gemini_api_key or self.groq_api_key)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
