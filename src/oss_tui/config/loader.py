"""Configuration file loading utilities."""

import tomllib
from pathlib import Path

from oss_tui.config.settings import AccountConfig, AppConfig
from oss_tui.exceptions import ConfigurationError

# Config file search paths in order of priority
CONFIG_PATHS = [
    Path.home() / ".config" / "oss-tui" / "config.toml",
    Path.home() / ".oss-tui.toml",
]


def find_config_file() -> Path | None:
    """Find the first existing configuration file.

    Returns:
        Path to the config file, or None if not found.
    """
    for path in CONFIG_PATHS:
        if path.exists():
            return path
    return None


def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from file.

    Args:
        path: Optional explicit path to config file.
              If not provided, searches default locations.

    Returns:
        Loaded application configuration.

    Raises:
        ConfigurationError: If the config file is invalid.
    """
    if path is None:
        path = find_config_file()

    if path is None:
        # Return default config if no file found
        return AppConfig()

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return AppConfig.model_validate(data)
    except tomllib.TOMLDecodeError as e:
        raise ConfigurationError(f"Invalid TOML in {path}: {e}") from e
    except Exception as e:
        raise ConfigurationError(f"Failed to load config from {path}: {e}") from e


def get_account_config(
    config: AppConfig, account_name: str | None = None
) -> tuple[str, AccountConfig]:
    """Get account configuration by name or use default.

    Args:
        config: The application configuration.
        account_name: Optional account name. If not provided, uses default.

    Returns:
        Tuple of (account_name, account_config).

    Raises:
        ConfigurationError: If the account is not found.
    """
    if account_name is None:
        account_name = config.default.account

    if account_name not in config.accounts:
        available = ", ".join(config.accounts.keys()) or "none"
        raise ConfigurationError(
            f"Account '{account_name}' not found. Available accounts: {available}"
        )

    return account_name, config.accounts[account_name]


def get_account_names(config: AppConfig) -> list[str]:
    """Get list of configured account names.

    Args:
        config: The application configuration.

    Returns:
        List of account names.
    """
    return list(config.accounts.keys())
