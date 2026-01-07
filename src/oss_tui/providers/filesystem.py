"""Filesystem provider for local development and testing."""

from datetime import datetime
from pathlib import Path

from oss_tui.exceptions import BucketNotFoundError, ObjectNotFoundError
from oss_tui.models.bucket import Bucket
from oss_tui.models.object import ListObjectsResult, Object


class FilesystemProvider:
    """OSS provider that uses the local filesystem.

    This provider treats top-level directories as "buckets"
    and files/subdirectories as "objects".
    """

    def __init__(self, root: str | None = None) -> None:
        """Initialize the filesystem provider.

        Args:
            root: Root directory to use. Defaults to home directory.
        """
        if root:
            self.root = Path(root).expanduser().resolve()
        else:
            self.root = Path.home()

    def list_buckets(self) -> list[Bucket]:
        """List top-level directories as buckets."""
        buckets = []
        for path in sorted(self.root.iterdir()):
            if path.is_dir() and not path.name.startswith("."):
                stat = path.stat()
                buckets.append(
                    Bucket(
                        name=path.name,
                        creation_date=datetime.fromtimestamp(stat.st_ctime),
                        location=str(self.root),
                    )
                )
        return buckets

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        delimiter: str = "/",
        max_keys: int = 100,
        marker: str | None = None,
    ) -> ListObjectsResult:
        """List files and directories in a bucket with pagination support.

        Args:
            bucket: The bucket name (top-level directory).
            prefix: Filter objects by prefix (subdirectory path).
            delimiter: Delimiter for directory-like listing.
            max_keys: Maximum number of objects to return (default 100).
            marker: Return objects after this key (exclusive).

        Returns:
            ListObjectsResult containing objects and pagination info.

        Raises:
            BucketNotFoundError: If the bucket does not exist.
        """
        bucket_path = self.root / bucket
        if not bucket_path.exists():
            raise BucketNotFoundError(f"Bucket not found: {bucket}")

        if prefix:
            target_path = bucket_path / prefix
        else:
            target_path = bucket_path

        if not target_path.exists():
            return ListObjectsResult(objects=[], is_truncated=False, next_marker=None)

        # Collect all objects first
        all_objects: list[Object] = []
        for path in sorted(target_path.iterdir()):
            if path.name.startswith("."):
                continue

            stat = path.stat()
            key = str(path.relative_to(bucket_path))
            if path.is_dir():
                key += "/"

            all_objects.append(
                Object(
                    key=key,
                    size=stat.st_size if path.is_file() else 0,
                    last_modified=datetime.fromtimestamp(stat.st_mtime),
                    is_directory=path.is_dir(),
                )
            )

        # Apply marker filter (exclusive - return objects after marker)
        if marker:
            filtered_objects = [obj for obj in all_objects if obj.key > marker]
        else:
            filtered_objects = all_objects

        # Apply pagination
        is_truncated = len(filtered_objects) > max_keys
        result_objects = filtered_objects[:max_keys]
        next_marker = result_objects[-1].key if is_truncated and result_objects else None

        return ListObjectsResult(
            objects=result_objects,
            is_truncated=is_truncated,
            next_marker=next_marker,
        )

    def get_object(self, bucket: str, key: str) -> bytes:
        """Read file content.

        Args:
            bucket: The bucket name.
            key: The object key.

        Returns:
            Object content as bytes.

        Raises:
            BucketNotFoundError: If the bucket does not exist.
            ObjectNotFoundError: If the object does not exist.
        """
        bucket_path = self.root / bucket
        if not bucket_path.exists():
            raise BucketNotFoundError(f"Bucket not found: {bucket}")

        path = bucket_path / key
        if not path.exists():
            raise ObjectNotFoundError(f"Object not found: {key}")

        return path.read_bytes()

    def put_object(self, bucket: str, key: str, data: bytes) -> Object:
        """Write file content."""
        path = self.root / bucket / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        stat = path.stat()
        return Object(
            key=key,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
        )

    def delete_object(self, bucket: str, key: str) -> None:
        """Delete a file or directory."""
        path = self.root / bucket / key
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()

    def copy_object(
        self,
        src_bucket: str,
        src_key: str,
        dst_bucket: str,
        dst_key: str,
    ) -> Object:
        """Copy a file."""
        import shutil

        src_path = self.root / src_bucket / src_key
        dst_path = self.root / dst_bucket / dst_key
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        stat = dst_path.stat()
        return Object(
            key=dst_key,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
        )
