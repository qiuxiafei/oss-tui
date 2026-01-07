"""Integration tests for the main OSS-TUI application."""

import pytest
from textual.app import App

from oss_tui.app import OssTuiApp
from oss_tui.config.settings import AppConfig, DefaultConfig, AccountConfig


class TestAppConfigLoading:
    """Test cases for app configuration loading."""

    def test_default_config_loading(self):
        """Test loading default configuration."""
        config = AppConfig()

        assert config.default.provider == "filesystem"
        assert config.default.account == "local"

    def test_custom_config_loading(self):
        """Test loading custom configuration."""
        config = AppConfig(
            default=DefaultConfig(provider="aliyun", account="test"),
        )

        assert config.default.provider == "aliyun"
        assert config.default.account == "test"

    def test_config_with_accounts(self):
        """Test configuration with multiple accounts."""
        config = AppConfig(
            default=DefaultConfig(provider="aliyun", account="personal"),
            accounts={
                "personal": AccountConfig(
                    provider="aliyun",
                    endpoint="oss-cn-hangzhou.aliyuncs.com",
                    access_key_id="key1",
                    access_key_secret="secret1",
                ),
                "work": AccountConfig(
                    provider="aliyun",
                    endpoint="oss-cn-shanghai.aliyuncs.com",
                    access_key_id="key2",
                    access_key_secret="secret2",
                ),
            },
        )

        assert len(config.accounts) == 2
        assert config.accounts["personal"].endpoint == "oss-cn-hangzhou.aliyuncs.com"
        assert config.accounts["work"].endpoint == "oss-cn-shanghai.aliyuncs.com"

    def test_empty_accounts(self):
        """Test configuration with no accounts."""
        config = AppConfig(
            default=DefaultConfig(provider="filesystem", account="local"),
            accounts={},
        )

        assert config.accounts == {}
        assert config.default.account == "local"


class TestDefaultConfig:
    """Test cases for DefaultConfig model."""

    def test_default_values(self):
        """Test DefaultConfig has correct default values."""
        config = DefaultConfig()

        assert config.provider == "filesystem"
        assert config.account == "local"

    def test_custom_values(self):
        """Test DefaultConfig with custom values."""
        config = DefaultConfig(provider="s3", account="aws")

        assert config.provider == "s3"
        assert config.account == "aws"


class TestAccountConfig:
    """Test cases for AccountConfig model."""

    def test_filesystem_account(self):
        """Test filesystem account configuration."""
        config = AccountConfig(
            provider="filesystem",
            root="/tmp",
        )

        assert config.provider == "filesystem"
        assert config.root == "/tmp"

    def test_aliyun_account(self):
        """Test aliyun account configuration."""
        config = AccountConfig(
            provider="aliyun",
            endpoint="oss-cn-hangzhou.aliyuncs.com",
            access_key_id="test-key",
            access_key_secret="test-secret",
        )

        assert config.provider == "aliyun"
        assert config.endpoint == "oss-cn-hangzhou.aliyuncs.com"
        assert config.access_key_id == "test-key"
        assert config.access_key_secret == "test-secret"

    def test_optional_fields(self):
        """Test account config with optional fields."""
        config = AccountConfig(provider="filesystem")

        assert config.root is None
        assert config.endpoint is None
        assert config.access_key_id is None
        assert config.access_key_secret is None
