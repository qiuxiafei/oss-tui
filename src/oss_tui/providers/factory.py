"""Provider factory for creating OSS providers from configuration."""

from typing import Protocol, runtime_checkable

from oss_tui.config.settings import AccountConfig
from oss_tui.exceptions import ConfigurationError
from oss_tui.models.bucket import Bucket
from oss_tui.models.object import ListObjectsResult, Object


@runtime_checkable
class OSSProviderProtocol(Protocol):
    """Protocol for OSS providers."""

    def list_buckets(self) -> list[Bucket]: ...
    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        delimiter: str = "/",
        max_keys: int = 100,
        marker: str | None = None,
    ) -> ListObjectsResult: ...
    def get_object(self, bucket: str, key: str) -> bytes: ...
    def put_object(self, bucket: str, key: str, data: bytes) -> Object: ...
    def delete_object(self, bucket: str, key: str) -> None: ...
    def copy_object(
        self, src_bucket: str, src_key: str, dst_bucket: str, dst_key: str
    ) -> Object: ...


# Registry of provider types to their factory functions
_PROVIDER_REGISTRY: dict[str, type] = {}


def register_provider(name: str, provider_class: type) -> None:
    """Register a provider class.

    Args:
        name: The provider type name (e.g., "filesystem", "aliyun").
        provider_class: The provider class to register.
    """
    _PROVIDER_REGISTRY[name] = provider_class


def get_registered_providers() -> list[str]:
    """Get list of registered provider type names.

    Returns:
        List of registered provider names.
    """
    return list(_PROVIDER_REGISTRY.keys())


def create_provider(account_config: AccountConfig) -> OSSProviderProtocol:
    """Create a provider instance from account configuration.

    Args:
        account_config: The account configuration.

    Returns:
        An instance of the appropriate provider.

    Raises:
        ConfigurationError: If the provider type is unknown or config is invalid.
    """
    provider_type = account_config.provider

    if provider_type not in _PROVIDER_REGISTRY:
        available = ", ".join(_PROVIDER_REGISTRY.keys()) or "none"
        raise ConfigurationError(
            f"Unknown provider type: {provider_type}. Available: {available}"
        )

    provider_class = _PROVIDER_REGISTRY[provider_type]

    try:
        if provider_type == "filesystem":
            return provider_class(root=account_config.root)
        elif provider_type == "aliyun":
            if not account_config.endpoint:
                raise ConfigurationError("Aliyun provider requires 'endpoint'")
            if not account_config.access_key_id:
                raise ConfigurationError("Aliyun provider requires 'access_key_id'")
            if not account_config.access_key_secret:
                raise ConfigurationError("Aliyun provider requires 'access_key_secret'")
            return provider_class(
                endpoint=account_config.endpoint,
                access_key_id=account_config.access_key_id,
                access_key_secret=account_config.access_key_secret,
            )
        else:
            # Generic instantiation for future providers
            raise ConfigurationError(
                f"Provider '{provider_type}' is registered but not yet implemented"
            )
    except TypeError as e:
        raise ConfigurationError(
            f"Invalid configuration for provider '{provider_type}': {e}"
        ) from e


def _register_default_providers() -> None:
    """Register built-in providers."""
    from oss_tui.providers.aliyun import AliyunOSSProvider
    from oss_tui.providers.filesystem import FilesystemProvider

    register_provider("filesystem", FilesystemProvider)
    register_provider("aliyun", AliyunOSSProvider)


# Auto-register default providers on module import
_register_default_providers()
