"""Tests for provider factory."""

from unittest.mock import MagicMock, patch

import pytest

from oss_tui.config.settings import AccountConfig
from oss_tui.exceptions import ConfigurationError
from oss_tui.providers.factory import (
    create_provider,
    get_registered_providers,
    register_provider,
)


class TestProviderRegistry:
    """Test cases for provider registry."""

    def test_get_registered_providers(self):
        """Test getting list of registered providers."""
        providers = get_registered_providers()

        assert "filesystem" in providers
        assert "aliyun" in providers

    def test_register_provider(self):
        """Test registering a new provider."""
        class DummyProvider:
            pass

        register_provider("dummy", DummyProvider)

        providers = get_registered_providers()
        assert "dummy" in providers


class TestCreateProvider:
    """Test cases for create_provider function."""

    def test_create_filesystem_provider(self):
        """Test creating filesystem provider."""
        config = AccountConfig(
            provider="filesystem",
            root="/tmp",
        )

        provider = create_provider(config)

        assert provider.__class__.__name__ == "FilesystemProvider"

    def test_create_filesystem_provider_default_root(self):
        """Test creating filesystem provider with default root."""
        config = AccountConfig(provider="filesystem")

        provider = create_provider(config)

        assert provider.__class__.__name__ == "FilesystemProvider"

    def test_create_aliyun_provider(self):
        """Test creating aliyun provider."""
        config = AccountConfig(
            provider="aliyun",
            endpoint="oss-cn-hangzhou.aliyuncs.com",
            access_key_id="test-key",
            access_key_secret="test-secret",
        )

        provider = create_provider(config)

        assert provider.__class__.__name__ == "AliyunOSSProvider"

    def test_create_unknown_provider(self):
        """Test creating unknown provider raises error."""
        config = AccountConfig(
            provider="unknown",
        )

        with pytest.raises(ConfigurationError) as exc_info:
            create_provider(config)

        assert "unknown" in str(exc_info.value)

    def test_create_aliyun_without_endpoint(self):
        """Test creating aliyun provider without endpoint raises error."""
        config = AccountConfig(
            provider="aliyun",
            access_key_id="key",
            access_key_secret="secret",
        )

        with pytest.raises(ConfigurationError) as exc_info:
            create_provider(config)

        assert "endpoint" in str(exc_info.value)

    def test_create_aliyun_without_access_key_id(self):
        """Test creating aliyun provider without access_key_id raises error."""
        config = AccountConfig(
            provider="aliyun",
            endpoint="endpoint",
            access_key_secret="secret",
        )

        with pytest.raises(ConfigurationError) as exc_info:
            create_provider(config)

        assert "access_key_id" in str(exc_info.value)

    def test_create_aliyun_without_access_key_secret(self):
        """Test creating aliyun provider without access_key_secret raises error."""
        config = AccountConfig(
            provider="aliyun",
            endpoint="endpoint",
            access_key_id="key",
        )

        with pytest.raises(ConfigurationError) as exc_info:
            create_provider(config)

        assert "access_key_secret" in str(exc_info.value)

    def test_create_provider_with_invalid_config(self):
        """Test creating provider with invalid config raises error."""
        config = AccountConfig(provider="unknown")

        with pytest.raises(ConfigurationError):
            create_provider(config)
