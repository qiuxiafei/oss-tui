"""Pydantic models for configuration."""

from pydantic import BaseModel


class AccountConfig(BaseModel):
    """Configuration for a single account."""

    provider: str
    endpoint: str | None = None
    access_key_id: str | None = None
    access_key_secret: str | None = None
    root: str | None = None  # For filesystem provider


class DefaultConfig(BaseModel):
    """Default configuration settings."""

    provider: str = "filesystem"
    account: str = "local"


class AppConfig(BaseModel):
    """Root configuration model."""

    default: DefaultConfig = DefaultConfig()
    accounts: dict[str, AccountConfig] = {}
