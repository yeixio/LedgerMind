"""Environment-backed settings."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ledgermind.exceptions import ConfigurationError


class Settings(BaseSettings):
    """LedgerMind configuration. Secrets come from the environment only."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ynab_access_token: str = ""
    ynab_budget_id: str | None = None

    ledgermind_cache_enabled: bool = False
    ledgermind_cache_path: Path = Path.home() / ".cache" / "ledgermind" / "cache.sqlite"
    ledgermind_minimum_buffer: int = 1000
    ledgermind_default_lookback_months: int = 6
    ledgermind_log_level: str = "INFO"
    ledgermind_debt_metadata_file: Path | None = None
    ledgermind_debug_log: bool = False

    @field_validator("ynab_access_token", mode="before")
    @classmethod
    def strip_token(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    def require_ynab_token(self) -> str:
        if not self.ynab_access_token:
            raise ConfigurationError(
                "YNAB_ACCESS_TOKEN is not set. Copy .env.example to .env and add your token."
            )
        return self.ynab_access_token


def load_settings() -> Settings:
    return Settings()
