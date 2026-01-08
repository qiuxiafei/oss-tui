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

    def test_download_directory(self, sample_filesystem: Path, temp_dir: Path):
        """Test downloading a directory."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        # Create a destination directory
        dest_dir = temp_dir / "downloads"
        dest_dir.mkdir()

        # Download subdir from bucket1
        progress_list = list(provider.download_directory(
            "bucket1", "subdir", str(dest_dir)
        ))

        # Check progress updates
        assert len(progress_list) >= 2  # At least initial and final progress
        final_progress = progress_list[-1]
        assert final_progress.completed_files == final_progress.total_files
        assert final_progress.total_files >= 1

        # Check downloaded files
        downloaded_file = dest_dir / "file3.txt"
        assert downloaded_file.exists()
        assert downloaded_file.read_text() == "content3"

    def test_download_directory_bucket_not_found(self, sample_filesystem: Path, temp_dir: Path):
        """Test downloading from non-existent bucket raises error."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        with pytest.raises(BucketNotFoundError):
            list(provider.download_directory("nonexistent", "subdir", str(temp_dir)))

    def test_download_directory_not_found(self, sample_filesystem: Path, temp_dir: Path):
        """Test downloading non-existent directory raises error."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        with pytest.raises(ObjectNotFoundError):
            list(provider.download_directory("bucket1", "nonexistent", str(temp_dir)))

    def test_upload_directory(self, sample_filesystem: Path, temp_dir: Path):
        """Test uploading a directory."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        # Create a source directory with files to upload
        src_dir = temp_dir / "to_upload"
        src_dir.mkdir()
        (src_dir / "upload1.txt").write_text("upload content 1")
        (src_dir / "upload2.txt").write_text("upload content 2")

        nested_dir = src_dir / "nested"
        nested_dir.mkdir()
        (nested_dir / "nested_file.txt").write_text("nested content")

        # Upload to bucket1
        progress_list = list(provider.upload_directory(
            "bucket1", str(src_dir), ""
        ))

        # Check progress updates
        assert len(progress_list) >= 2  # At least initial and final progress
        final_progress = progress_list[-1]
        assert final_progress.completed_files == final_progress.total_files
        assert final_progress.total_files == 3  # 3 files uploaded

        # Check uploaded files
        uploaded_dir = sample_filesystem / "bucket1" / "to_upload"
        assert uploaded_dir.exists()
        assert (uploaded_dir / "upload1.txt").read_text() == "upload content 1"
        assert (uploaded_dir / "upload2.txt").read_text() == "upload content 2"
        assert (uploaded_dir / "nested" / "nested_file.txt").read_text() == "nested content"

    def test_upload_directory_with_prefix(self, sample_filesystem: Path, temp_dir: Path):
        """Test uploading a directory with a prefix."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        # Create a source directory with a file
        src_dir = temp_dir / "upload_with_prefix"
        src_dir.mkdir()
        (src_dir / "test.txt").write_text("test content")

        # Upload to bucket1 with prefix
        progress_list = list(provider.upload_directory(
            "bucket1", str(src_dir), "target_dir/"
        ))

        # Check final progress
        final_progress = progress_list[-1]
        assert final_progress.completed_files == 1

        # Check uploaded file is in the right place
        uploaded_file = sample_filesystem / "bucket1" / "target_dir" / "upload_with_prefix" / "test.txt"
        assert uploaded_file.exists()
        assert uploaded_file.read_text() == "test content"

    def test_upload_directory_not_found(self, sample_filesystem: Path, temp_dir: Path):
        """Test uploading non-existent directory raises error."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        with pytest.raises(FileNotFoundError):
            list(provider.upload_directory("bucket1", str(temp_dir / "nonexistent"), ""))

    def test_upload_directory_bucket_not_found(self, sample_filesystem: Path, temp_dir: Path):
        """Test uploading to non-existent bucket raises error."""
        provider = FilesystemProvider(root=str(sample_filesystem))

        # Create a source directory
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")

        with pytest.raises(BucketNotFoundError):
            list(provider.upload_directory("nonexistent", str(src_dir), ""))
