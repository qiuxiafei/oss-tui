"""Tests for configuration loading."""

from pathlib import Path

import pytest

from oss_tui.config.loader import load_config
from oss_tui.config.settings import AppConfig
from oss_tui.exceptions import ConfigurationError


class TestConfigLoader:
    """Test cases for configuration loading."""

    def test_load_default_config(self):
        """Test loading default config when no file exists."""
        config = load_config(path=None)

        assert isinstance(config, AppConfig)
        assert config.default.provider == "filesystem"
        assert config.default.account == "local"

    def test_load_config_from_file(self, temp_dir: Path):
        """Test loading config from a TOML file."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
provider = "aliyun"
account = "test"

[accounts.test]
provider = "aliyun"
endpoint = "oss-cn-hangzhou.aliyuncs.com"
access_key_id = "test-key"
access_key_secret = "test-secret"
""")

        config = load_config(path=config_file)

        assert config.default.provider == "aliyun"
        assert config.default.account == "test"
        assert "test" in config.accounts
        assert config.accounts["test"].endpoint == "oss-cn-hangzhou.aliyuncs.com"

    def test_load_invalid_toml(self, temp_dir: Path):
        """Test that invalid TOML raises ConfigurationError."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("invalid toml [[[")

        with pytest.raises(ConfigurationError):
            load_config(path=config_file)
