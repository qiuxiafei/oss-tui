"""Configuration file loading utilities."""

import tomllib
from pathlib import Path

from oss_tui.config.settings import AppConfig
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
