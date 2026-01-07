"""Tests for FilesystemProvider."""

from pathlib import Path

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
        objects = provider.list_objects("bucket1")

        names = [o.name for o in objects]
        assert "file1.txt" in names
        assert "file2.txt" in names
        assert "subdir" in names

    def test_list_objects_in_subdir(self, sample_filesystem: Path):
        """Test listing objects in a subdirectory."""
        provider = FilesystemProvider(root=str(sample_filesystem))
        objects = provider.list_objects("bucket1", prefix="subdir")

        assert len(objects) == 1
        assert objects[0].name == "file3.txt"

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
