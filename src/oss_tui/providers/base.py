"""Abstract base for OSS providers."""

from typing import Protocol

from oss_tui.models.bucket import Bucket
from oss_tui.models.object import Object


class OSSProvider(Protocol):
    """Protocol defining the interface for OSS providers.

    All OSS providers must implement this interface to ensure
    consistent behavior across different storage backends.
    """

    def list_buckets(self) -> list[Bucket]:
        """List all available buckets.

        Returns:
            List of Bucket objects.
        """
        ...

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        delimiter: str = "/",
    ) -> list[Object]:
        """List objects in a bucket.

        Args:
            bucket: The bucket name.
            prefix: Filter objects by prefix (path).
            delimiter: Delimiter for directory-like listing.

        Returns:
            List of Object objects.
        """
        ...

    def get_object(self, bucket: str, key: str) -> bytes:
        """Get object content.

        Args:
            bucket: The bucket name.
            key: The object key.

        Returns:
            Object content as bytes.
        """
        ...

    def put_object(self, bucket: str, key: str, data: bytes) -> Object:
        """Upload an object.

        Args:
            bucket: The bucket name.
            key: The object key.
            data: The content to upload.

        Returns:
            The uploaded Object metadata.
        """
        ...

    def delete_object(self, bucket: str, key: str) -> None:
        """Delete an object.

        Args:
            bucket: The bucket name.
            key: The object key.
        """
        ...

    def copy_object(
        self,
        src_bucket: str,
        src_key: str,
        dst_bucket: str,
        dst_key: str,
    ) -> Object:
        """Copy an object.

        Args:
            src_bucket: Source bucket name.
            src_key: Source object key.
            dst_bucket: Destination bucket name.
            dst_key: Destination object key.

        Returns:
            The copied Object metadata.
        """
        ...
