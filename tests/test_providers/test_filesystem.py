"""Tests for FilesystemProvider."""

from pathlib import Path

import pytest

from oss_tui.exceptions import BucketNotFoundError, ObjectNotFoundError
from oss_tui.providers.filesystem import FilesystemProvider


class TestFilesystemProvider:
    """Test cases for FilesystemProvider."""

    def test_list_buckets(self, sample_filesystem: Path):
        """Test listing buckets (top-level directories)."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        buckets = provider.list_buckets()

        names = [b.name for b in buckets]
        assert "bucket1" in names
        assert "bucket2" in names
        assert len(buckets) == 2

    def test_list_objects(self, sample_filesystem: Path):
        """Test listing objects in a bucket."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        result = provider.list_objects("bucket1")

        names = [o.name for o in result.objects]
        assert "file1.txt" in names
        assert "file2.txt" in names
        assert "subdir" in names
        assert result.is_truncated is False
        assert result.next_marker is None

    def test_list_objects_in_subdir(self, sample_filesystem: Path):
        """Test listing objects in a subdirectory."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        result = provider.list_objects("bucket1", prefix="subdir")

        assert len(result.objects) == 1
        assert result.objects[0].name == "file3.txt"

    def test_get_object(self, sample_filesystem: Path):
        """Test reading object content."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        content = provider.get_object("bucket1", "file1.txt")

        assert content == b"content1"

    def test_put_object(self, sample_filesystem: Path):
        """Test writing object content."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        obj = provider.put_object("bucket1", "new_file.txt", b"new content")

        assert obj.key == "new_file.txt"
        assert (sample_filesystem / "bucket1" / "new_file.txt").exists()
        assert (sample_filesystem / "bucket1" / "new_file.txt").read_text() == "new content"

    def test_delete_object(self, sample_filesystem: Path):
        """Test deleting an object."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        provider.delete_object("bucket1", "file1.txt")

        assert not (sample_filesystem / "bucket1" / "file1.txt").exists()

    def test_copy_object(self, sample_filesystem: Path):
        """Test copying an object."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        obj = provider.copy_object("bucket1", "file1.txt", "bucket2", "copied.txt")

        assert obj.key == "copied.txt"
        assert (sample_filesystem / "bucket2" / "copied.txt").exists()
        assert (sample_filesystem / "bucket2" / "copied.txt").read_text() == "content1"

    def test_list_objects_pagination_max_keys(self, sample_filesystem: Path):
        """Test pagination with max_keys limit."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        result = provider.list_objects("bucket1", max_keys=2)

        assert len(result.objects) == 2
        assert result.is_truncated is True
        assert result.next_marker is not None

    def test_list_objects_pagination_marker(self, sample_filesystem: Path):
        """Test pagination with marker (exclusive)."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        # First page
        result1 = provider.list_objects("bucket1", max_keys=1)
        assert len(result1.objects) == 1
        first_key = result1.objects[0].key
        assert result1.is_truncated is True

        # Second page using marker
        result2 = provider.list_objects("bucket1", max_keys=1, marker=first_key)
        assert len(result2.objects) == 1
        # Marker is exclusive, so second object should be different
        assert result2.objects[0].key != first_key
        assert result2.objects[0].key > first_key

    def test_list_objects_pagination_all_pages(self, sample_filesystem: Path):
        """Test iterating through all pages."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        all_objects = []
        marker = None
        while True:
            result = provider.list_objects("bucket1", max_keys=1, marker=marker)
            all_objects.extend(result.objects)
            if not result.is_truncated:
                break
            marker = result.next_marker

        # bucket1 has: file1.txt, file2.txt, subdir/
        assert len(all_objects) == 3
        names = [o.name for o in all_objects]
        assert "file1.txt" in names
        assert "file2.txt" in names
        assert "subdir" in names

    def test_list_objects_bucket_not_found(self, sample_filesystem: Path):
        """Test that BucketNotFoundError is raised for non-existent bucket."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        with pytest.raises(BucketNotFoundError):
            provider.list_objects("nonexistent_bucket")

    def test_list_objects_nonexistent_prefix(self, sample_filesystem: Path):
        """Test listing objects with non-existent prefix returns empty result."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        result = provider.list_objects("bucket1", prefix="nonexistent")

        assert result.objects == []
        assert result.is_truncated is False
        assert result.next_marker is None

    def test_get_object_bucket_not_found(self, sample_filesystem: Path):
        """Test that BucketNotFoundError is raised for non-existent bucket."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        with pytest.raises(BucketNotFoundError):
            provider.get_object("nonexistent_bucket", "file.txt")

    def test_get_object_not_found(self, sample_filesystem: Path):
        """Test that ObjectNotFoundError is raised for non-existent object."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        with pytest.raises(ObjectNotFoundError):
            provider.get_object("bucket1", "nonexistent_file.txt")
