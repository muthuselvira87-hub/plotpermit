from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    app_name: str = "PlotPermit"
    environment: str = "local"

    # Gemini API settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    fallback_model: str = "gemini-3.6-flash"

    # PostgreSQL database settings
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()