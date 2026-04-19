from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Locale = Literal["ru", "en"]
Units = Literal["metric", "imperial"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: SecretStr = Field(..., description="Telegram bot token from @BotFather")
    openweather_api_key: SecretStr = Field(..., description="OpenWeather API key")

    database_url: str = Field(default="sqlite+aiosqlite:///./data/bot.db")
    default_locale: Locale = Field(default="ru")
    default_units: Units = Field(default="metric")
    log_level: str = Field(default="INFO")
    drop_pending_updates: bool = Field(default=False)
    weather_cache_ttl: int = Field(default=300, ge=0, le=3600)

    def ensure_dirs(self) -> None:
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.split("///", 1)[-1]
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
