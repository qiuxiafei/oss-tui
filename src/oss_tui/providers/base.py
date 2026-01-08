"""Abstract base for OSS providers."""

from collections.abc import Generator
from typing import Protocol

from oss_tui.models.bucket import Bucket
from oss_tui.models.object import ListObjectsResult, Object


class TransferProgress:
    """Progress information for directory transfer operations.

    Attributes:
        total_files: Total number of files to transfer.
        completed_files: Number of files transferred so far.
        current_file: Path of the file currently being transferred.
        total_bytes: Total bytes to transfer (if known).
        transferred_bytes: Bytes transferred so far.
    """

    def __init__(
        self,
        total_files: int = 0,
        completed_files: int = 0,
        current_file: str = "",
        total_bytes: int = 0,
        transferred_bytes: int = 0,
    ) -> None:
        self.total_files = total_files
        self.completed_files = completed_files
        self.current_file = current_file
        self.total_bytes = total_bytes
        self.transferred_bytes = transferred_bytes

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage based on file count."""
        if self.total_files == 0:
            return 0.0
        return (self.completed_files / self.total_files) * 100


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
        max_keys: int = 100,
        marker: str | None = None,
    ) -> ListObjectsResult:
        """List objects in a bucket with pagination support.

        Args:
            bucket: The bucket name.
            prefix: Filter objects by prefix (path).
            delimiter: Delimiter for directory-like listing.
            max_keys: Maximum number of objects to return (default 100).
            marker: Return objects after this key (exclusive).

        Returns:
            ListObjectsResult containing objects and pagination info.
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

    def download_directory(
        self,
        bucket: str,
        prefix: str,
        local_path: str,
    ) -> Generator[TransferProgress, None, None]:
        """Download a directory from the bucket to a local path.

        Downloads all objects under the given prefix to the local directory,
        preserving the directory structure.

        Args:
            bucket: The bucket name.
            prefix: The prefix (directory) to download.
            local_path: The local directory path to save files to.

        Yields:
            TransferProgress objects indicating download progress.

        Raises:
            BucketNotFoundError: If the bucket does not exist.
            OSSError: If there is an error downloading files.
        """
        ...

    def upload_directory(
        self,
        bucket: str,
        local_path: str,
        prefix: str = "",
    ) -> Generator[TransferProgress, None, None]:
        """Upload a local directory to the bucket.

        Uploads all files in the local directory to the bucket,
        preserving the directory structure.

        Args:
            bucket: The bucket name.
            local_path: The local directory path to upload.
            prefix: The prefix (directory) to upload to in the bucket.

        Yields:
            TransferProgress objects indicating upload progress.

        Raises:
            BucketNotFoundError: If the bucket does not exist.
            FileNotFoundError: If the local path does not exist.
            OSSError: If there is an error uploading files.
        """
        ...
