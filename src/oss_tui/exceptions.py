"""Custom exceptions for OSS-TUI."""


class OSSError(Exception):
    """Base exception for OSS operations."""


class BucketNotFoundError(OSSError):
    """Raised when the specified bucket does not exist."""


class ObjectNotFoundError(OSSError):
    """Raised when the specified object does not exist."""


class AuthenticationError(OSSError):
    """Raised when authentication fails."""


class PermissionDeniedError(OSSError):
    """Raised when the user lacks permission for an operation."""


class ConfigurationError(Exception):
    """Raised when there is a configuration error."""
