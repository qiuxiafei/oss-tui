"""Tests for configuration loading."""

from pathlib import Path

import pytest

from oss_tui.config.loader import (
    get_account_config,
    get_account_names,
    load_config,
)
from oss_tui.config.settings import AppConfig, DefaultConfig
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

    def test_load_config_with_filesystem_account(self, temp_dir: Path):
        """Test loading config with filesystem account."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
provider = "filesystem"
account = "local"

[accounts.local]
provider = "filesystem"
root = "/tmp"
""")

        config = load_config(path=config_file)

        assert config.accounts["local"].provider == "filesystem"
        assert config.accounts["local"].root == "/tmp"

    def test_load_config_with_multiple_accounts(self, temp_dir: Path):
        """Test loading config with multiple accounts."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
provider = "aliyun"
account = "personal"

[accounts.personal]
provider = "aliyun"
endpoint = "oss-cn-hangzhou.aliyuncs.com"
access_key_id = "key1"
access_key_secret = "secret1"

[accounts.work]
provider = "aliyun"
endpoint = "oss-cn-shanghai.aliyuncs.com"
access_key_id = "key2"
access_key_secret = "secret2"
""")

        config = load_config(path=config_file)

        assert len(config.accounts) == 2
        assert config.accounts["personal"].endpoint == "oss-cn-hangzhou.aliyuncs.com"
        assert config.accounts["work"].endpoint == "oss-cn-shanghai.aliyuncs.com"


class TestGetAccountNames:
    """Test cases for get_account_names function."""

    def test_get_account_names_empty(self):
        """Test getting account names from empty config."""
        config = AppConfig()
        names = get_account_names(config)
        assert names == []

    def test_get_account_names_with_accounts(self, temp_dir: Path):
        """Test getting account names from config with accounts."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
account = "account1"

[accounts.account1]
provider = "filesystem"

[accounts.account2]
provider = "filesystem"
""")

        config = load_config(path=config_file)
        names = get_account_names(config)

        assert len(names) == 2
        assert "account1" in names
        assert "account2" in names


class TestGetAccountConfig:
    """Test cases for get_account_config function."""

    def test_get_account_config_by_name(self, temp_dir: Path):
        """Test getting account config by name."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
account = "local"

[accounts.local]
provider = "filesystem"
root = "/home/user"
""")

        config = load_config(path=config_file)
        name, acc = get_account_config(config, "local")

        assert name == "local"
        assert acc.provider == "filesystem"
        assert acc.root == "/home/user"

    def test_get_account_config_uses_default(self, temp_dir: Path):
        """Test that default account is used when not specified."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
account = "myaccount"

[accounts.myaccount]
provider = "filesystem"
""")

        config = load_config(path=config_file)
        name, acc = get_account_config(config)

        assert name == "myaccount"

    def test_get_account_config_not_found(self, temp_dir: Path):
        """Test that missing account raises ConfigurationError."""
        config_file = temp_dir / "config.toml"
        config_file.write_text("""
[default]
account = "existing"

[accounts.existing]
provider = "filesystem"
""")

        config = load_config(path=config_file)

        with pytest.raises(ConfigurationError) as exc_info:
            get_account_config(config, "nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert "existing" in str(exc_info.value)


class TestAppConfig:
    """Test cases for AppConfig model."""

    def test_default_values(self):
        """Test that AppConfig has correct default values."""
        config = AppConfig()

        assert config.default.provider == "filesystem"
        assert config.default.account == "local"
        assert config.accounts == {}

    def test_custom_default_config(self):
        """Test creating AppConfig with custom defaults."""
        config = AppConfig(
            default=DefaultConfig(provider="aliyun", account="test"),
        )

        assert config.default.provider == "aliyun"
        assert config.default.account == "test"

