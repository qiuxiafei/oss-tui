"""Alibaba Cloud OSS provider."""

from collections.abc import Callable, Generator
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from typing import TypeVar

import oss2
import oss2.exceptions

from oss_tui.exceptions import (
    AuthenticationError,
    BucketNotFoundError,
    ObjectNotFoundError,
    OSSError,
    PermissionDeniedError,
)
from oss_tui.models.bucket import Bucket
from oss_tui.models.object import ListObjectsResult, Object
from oss_tui.providers.base import TransferProgress

T = TypeVar("T")


def _handle_oss_exceptions(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to convert oss2 exceptions to custom exceptions."""

    @wraps(func)
    def wrapper(*args: object, **kwargs: object) -> T:
        try:
            return func(*args, **kwargs)
        except oss2.exceptions.NoSuchBucket as e:
            bucket_name = e.details.get("BucketName", "") if e.details else ""
            raise BucketNotFoundError(f"Bucket not found: {bucket_name}") from e
        except oss2.exceptions.NoSuchKey as e:
            key = e.details.get("Key", "") if e.details else ""
            raise ObjectNotFoundError(f"Object not found: {key}") from e
        except oss2.exceptions.AccessDenied as e:
            raise PermissionDeniedError(f"Access denied: {e.message}") from e
        except oss2.exceptions.SignatureDoesNotMatch:
            raise AuthenticationError("Invalid access key secret") from None
        except oss2.exceptions.ServerError as e:
            # Handle InvalidAccessKeyId via error code
            if e.code == "InvalidAccessKeyId":
                raise AuthenticationError("Invalid access key ID") from None
            raise OSSError(f"OSS error: {e.message}") from e
        except oss2.exceptions.OssError as e:
            raise OSSError(f"OSS error: {getattr(e, 'message', str(e))}") from e

    return wrapper


class AliyunOSSProvider:
    """OSS provider for Alibaba Cloud OSS.

    Supports cross-region bucket access by automatically detecting
    bucket locations and using the correct endpoint.
    """

    def __init__(
        self,
        endpoint: str,
        access_key_id: str,
        access_key_secret: str,
    ) -> None:
        """Initialize the Aliyun OSS provider.

        Args:
            endpoint: OSS endpoint (e.g., oss-cn-hangzhou.aliyuncs.com).
            access_key_id: Access key ID.
            access_key_secret: Access key secret.
        """
        # Normalize endpoint to include https://
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        self.endpoint = endpoint

        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.service = oss2.Service(self.auth, endpoint)

        # Bucket object cache (key: bucket_name, value: oss2.Bucket)
        # TODO: Optimize with LRU cache or TTL-based cache
        self._bucket_cache: dict[str, oss2.Bucket] = {}

        # Bucket location cache (for cross-region access)
        self._bucket_locations: dict[str, str] = {}

    def _get_bucket_endpoint(self, bucket_name: str) -> str:
        """Get the correct endpoint for a bucket based on its location.

        Args:
            bucket_name: The bucket name.

        Returns:
            The endpoint URL for the bucket's region.
        """
        if bucket_name not in self._bucket_locations:
            # Use default endpoint to fetch bucket info first
            temp_bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
            info = temp_bucket.get_bucket_info()
            self._bucket_locations[bucket_name] = info.location

        location = self._bucket_locations[bucket_name]
        return f"https://{location}.aliyuncs.com"

    def _get_bucket(self, bucket_name: str) -> oss2.Bucket:
        """Get a cached Bucket object with the correct endpoint.

        Args:
            bucket_name: The bucket name.

        Returns:
            An oss2.Bucket object configured for the correct region.
        """
        if bucket_name not in self._bucket_cache:
            endpoint = self._get_bucket_endpoint(bucket_name)
            self._bucket_cache[bucket_name] = oss2.Bucket(
                self.auth, endpoint, bucket_name
            )
        return self._bucket_cache[bucket_name]

    @_handle_oss_exceptions
    def list_buckets(self) -> list[Bucket]:
        """List all buckets.

        Returns:
            List of Bucket objects.
        """
        buckets: list[Bucket] = []

        for b in oss2.BucketIterator(self.service):
            # Cache location for future use
            self._bucket_locations[b.name] = b.location

            buckets.append(
                Bucket(
                    name=b.name,
                    creation_date=datetime.fromtimestamp(b.creation_date, tz=UTC),
                    location=b.location,
                )
            )

        return buckets

    @_handle_oss_exceptions
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
            max_keys: Maximum number of objects to return.
            marker: Return objects after this key (exclusive).

        Returns:
            ListObjectsResult containing objects and pagination info.
        """
        bucket_obj = self._get_bucket(bucket)
        result = bucket_obj.list_objects(
            prefix=prefix,
            delimiter=delimiter,
            max_keys=max_keys,
            marker=marker or "",
        )

        objects: list[Object] = []

        # Common prefixes (directories) from delimiter grouping
        for cp in result.prefix_list:
            objects.append(
                Object(
                    key=cp,
                    is_directory=True,
                )
            )

        # Objects (files and directory placeholders)
        for obj in result.object_list:
            # OSS directory placeholders: end with "/" and have size 0
            if obj.key.endswith("/") and obj.size == 0:
                objects.append(
                    Object(
                        key=obj.key,
                        is_directory=True,
                    )
                )
            else:
                objects.append(
                    Object(
                        key=obj.key,
                        size=obj.size,
                        last_modified=datetime.fromtimestamp(
                            obj.last_modified, tz=UTC
                        ),
                        etag=obj.etag.strip('"') if obj.etag else None,
                    )
                )

        return ListObjectsResult(
            objects=objects,
            is_truncated=result.is_truncated,
            next_marker=result.next_marker,
        )

    @_handle_oss_exceptions
    def get_object(self, bucket: str, key: str) -> bytes:
        """Get object content.

        Args:
            bucket: The bucket name.
            key: The object key.

        Returns:
            Object content as bytes.

        Note:
            TODO: Support streaming for large files to avoid memory issues.
        """
        bucket_obj = self._get_bucket(bucket)
        result = bucket_obj.get_object(key)
        content = result.read()
        # oss2 lacks proper type hints; read() always returns bytes
        return content  # type: ignore[return-value]

    @_handle_oss_exceptions
    def put_object(self, bucket: str, key: str, data: bytes) -> Object:
        """Upload an object.

        Args:
            bucket: The bucket name.
            key: The object key.
            data: The content to upload.

        Returns:
            The uploaded Object metadata.
        """
        bucket_obj = self._get_bucket(bucket)
        bucket_obj.put_object(key, data)

        # Fetch metadata after upload
        meta = bucket_obj.head_object(key)
        return Object(
            key=key,
            size=meta.content_length,
            last_modified=datetime.fromtimestamp(meta.last_modified, tz=UTC),
            etag=meta.etag.strip('"') if meta.etag else None,
            content_type=meta.content_type,
        )

    @_handle_oss_exceptions
    def delete_object(self, bucket: str, key: str) -> None:
        """Delete an object.

        Args:
            bucket: The bucket name.
            key: The object key.
        """
        bucket_obj = self._get_bucket(bucket)
        bucket_obj.delete_object(key)

    @_handle_oss_exceptions
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
        dst_bucket_obj = self._get_bucket(dst_bucket)

        # Copy object (works for cross-bucket copies)
        dst_bucket_obj.copy_object(src_bucket, src_key, dst_key)

        # Fetch metadata after copy
        meta = dst_bucket_obj.head_object(dst_key)
        return Object(
            key=dst_key,
            size=meta.content_length,
            last_modified=datetime.fromtimestamp(meta.last_modified, tz=UTC),
            etag=meta.etag.strip('"') if meta.etag else None,
            content_type=meta.content_type,
        )

    def _list_all_objects(
        self, bucket: str, prefix: str = ""
    ) -> list[tuple[str, int]]:
        """List all objects under a prefix recursively.

        Args:
            bucket: The bucket name.
            prefix: The prefix to list objects under.

        Returns:
            List of tuples containing (key, size) for each object.
        """
        bucket_obj = self._get_bucket(bucket)
        objects: list[tuple[str, int]] = []

        marker = ""
        while True:
            result = bucket_obj.list_objects(
                prefix=prefix,
                delimiter="",  # No delimiter to get all nested objects
                marker=marker,
                max_keys=1000,
            )

            for obj in result.object_list:
                # Skip directory placeholder objects
                if not (obj.key.endswith("/") and obj.size == 0):
                    objects.append((obj.key, obj.size))

            if not result.is_truncated:
                break
            marker = result.next_marker

        return objects

    @_handle_oss_exceptions
    def download_directory(
        self,
        bucket: str,
        prefix: str,
        local_path: str,
    ) -> Generator[TransferProgress, None, None]:
        """Download a directory from the bucket to a local path.

        Args:
            bucket: The bucket name.
            prefix: The prefix (directory) to download.
            local_path: The local directory path to save files to.

        Yields:
            TransferProgress objects indicating download progress.
        """
        bucket_obj = self._get_bucket(bucket)

        # Destination directory
        dst_dir = Path(local_path).expanduser()
        dst_dir.mkdir(parents=True, exist_ok=True)

        # List all objects under the prefix
        objects = self._list_all_objects(bucket, prefix)
        total_files = len(objects)
        total_bytes = sum(size for _, size in objects)
        transferred_bytes = 0

        # Yield initial progress
        yield TransferProgress(
            total_files=total_files,
            completed_files=0,
            current_file="",
            total_bytes=total_bytes,
            transferred_bytes=0,
        )

        # Normalize prefix for relative path calculation
        prefix_normalized = prefix.rstrip("/")

        # Download each object
        for i, (key, size) in enumerate(objects):
            # Calculate relative path (remove prefix)
            if prefix_normalized:
                relative_key = key[len(prefix_normalized) :].lstrip("/")
            else:
                relative_key = key

            dst_file = dst_dir / relative_key

            # Yield progress before starting this file
            yield TransferProgress(
                total_files=total_files,
                completed_files=i,
                current_file=relative_key,
                total_bytes=total_bytes,
                transferred_bytes=transferred_bytes,
            )

            # Create parent directory and download file
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            obj_result = bucket_obj.get_object(key)
            file_content = obj_result.read()
            # oss2 lacks proper type hints; read() always returns bytes
            dst_file.write_bytes(file_content)  # type: ignore[arg-type]

            transferred_bytes += size

        # Yield final progress
        yield TransferProgress(
            total_files=total_files,
            completed_files=total_files,
            current_file="",
            total_bytes=total_bytes,
            transferred_bytes=transferred_bytes,
        )

    @_handle_oss_exceptions
    def upload_directory(
        self,
        bucket: str,
        local_path: str,
        prefix: str = "",
    ) -> Generator[TransferProgress, None, None]:
        """Upload a local directory to the bucket.

        Args:
            bucket: The bucket name.
            local_path: The local directory path to upload.
            prefix: The prefix (directory) to upload to in the bucket.

        Yields:
            TransferProgress objects indicating upload progress.
        """
        bucket_obj = self._get_bucket(bucket)

        # Source directory
        src_dir = Path(local_path).expanduser()
        if not src_dir.exists():
            raise FileNotFoundError(f"Local directory not found: {local_path}")
        if not src_dir.is_dir():
            raise ValueError(f"Not a directory: {local_path}")

        # Collect all files to upload
        files_to_upload: list[Path] = []
        total_bytes = 0
        for src_file in src_dir.rglob("*"):
            if src_file.is_file() and not src_file.name.startswith("."):
                files_to_upload.append(src_file)
                total_bytes += src_file.stat().st_size

        total_files = len(files_to_upload)
        transferred_bytes = 0

        # Yield initial progress
        yield TransferProgress(
            total_files=total_files,
            completed_files=0,
            current_file="",
            total_bytes=total_bytes,
            transferred_bytes=0,
        )

        # Calculate base prefix (include source directory name)
        if prefix:
            base_prefix = prefix.rstrip("/") + "/" + src_dir.name + "/"
        else:
            base_prefix = src_dir.name + "/"

        # Upload each file
        for i, src_file in enumerate(files_to_upload):
            relative_path = src_file.relative_to(src_dir)
            remote_key = base_prefix + str(relative_path).replace("\\", "/")

            # Yield progress before starting this file
            yield TransferProgress(
                total_files=total_files,
                completed_files=i,
                current_file=str(relative_path),
                total_bytes=total_bytes,
                transferred_bytes=transferred_bytes,
            )

            # Upload file
            content = src_file.read_bytes()
            bucket_obj.put_object(remote_key, content)

            transferred_bytes += src_file.stat().st_size

        # Yield final progress
        yield TransferProgress(
            total_files=total_files,
            completed_files=total_files,
            current_file="",
            total_bytes=total_bytes,
            transferred_bytes=transferred_bytes,
        )
