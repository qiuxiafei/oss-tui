"""Unit tests for AliyunOSSProvider using mocks."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from oss_tui.exceptions import (
    AuthenticationError,
    BucketNotFoundError,
    ObjectNotFoundError,
    PermissionDeniedError,
)
from oss_tui.providers.aliyun import AliyunOSSProvider


@pytest.fixture
def mock_oss2():
    """Create a mock oss2 module, preserving real exceptions."""
    import oss2.exceptions

    with patch("oss_tui.providers.aliyun.oss2") as mock:
        # Preserve the real exceptions module for proper exception handling
        mock.exceptions = oss2.exceptions
        yield mock


@pytest.fixture
def provider(mock_oss2):
    """Create a provider instance with mocked oss2."""
    return AliyunOSSProvider(
        endpoint="oss-cn-hangzhou.aliyuncs.com",
        access_key_id="test-key-id",
        access_key_secret="test-key-secret",
    )


class TestAliyunOSSProviderInit:
    """Tests for provider initialization."""

    def test_init_without_https(self, mock_oss2):
        """Test that endpoint is normalized to include https://."""
        provider = AliyunOSSProvider(
            endpoint="oss-cn-hangzhou.aliyuncs.com",
            access_key_id="key-id",
            access_key_secret="key-secret",
        )
        assert provider.endpoint == "https://oss-cn-hangzhou.aliyuncs.com"

    def test_init_with_https(self, mock_oss2):
        """Test that endpoint with https:// is preserved."""
        provider = AliyunOSSProvider(
            endpoint="https://oss-cn-hangzhou.aliyuncs.com",
            access_key_id="key-id",
            access_key_secret="key-secret",
        )
        assert provider.endpoint == "https://oss-cn-hangzhou.aliyuncs.com"

    def test_init_creates_auth_and_service(self, mock_oss2):
        """Test that Auth and Service are created correctly."""
        AliyunOSSProvider(
            endpoint="oss-cn-hangzhou.aliyuncs.com",
            access_key_id="key-id",
            access_key_secret="key-secret",
        )

        mock_oss2.Auth.assert_called_once_with("key-id", "key-secret")
        mock_oss2.Service.assert_called_once()


class TestListBuckets:
    """Tests for list_buckets method."""

    def test_list_buckets_returns_buckets(self, provider, mock_oss2):
        """Test that list_buckets returns correct bucket list."""
        # Setup mock bucket
        mock_bucket = MagicMock()
        mock_bucket.name = "test-bucket"
        mock_bucket.creation_date = 1704067200  # 2024-01-01 00:00:00 UTC
        mock_bucket.location = "cn-hangzhou"

        mock_oss2.BucketIterator.return_value = [mock_bucket]

        buckets = provider.list_buckets()

        assert len(buckets) == 1
        assert buckets[0].name == "test-bucket"
        assert buckets[0].location == "cn-hangzhou"
        assert buckets[0].creation_date == datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)

    def test_list_buckets_caches_location(self, provider, mock_oss2):
        """Test that bucket location is cached after listing."""
        mock_bucket = MagicMock()
        mock_bucket.name = "test-bucket"
        mock_bucket.creation_date = 1704067200
        mock_bucket.location = "cn-shanghai"

        mock_oss2.BucketIterator.return_value = [mock_bucket]

        provider.list_buckets()

        assert provider._bucket_locations["test-bucket"] == "cn-shanghai"

    def test_list_buckets_empty(self, provider, mock_oss2):
        """Test list_buckets with no buckets."""
        mock_oss2.BucketIterator.return_value = []

        buckets = provider.list_buckets()

        assert buckets == []


class TestListObjects:
    """Tests for list_objects method."""

    def test_list_objects_returns_files_and_directories(self, provider, mock_oss2):
        """Test that list_objects returns both files and directories."""
        # Setup mock bucket and result
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj

        mock_result = MagicMock()
        mock_result.prefix_list = ["folder1/"]
        mock_result.object_list = [
            MagicMock(key="file1.txt", size=100, last_modified=1704067200, etag='"abc123"'),
            MagicMock(key="folder2/", size=0, last_modified=1704067200, etag='""'),
        ]
        mock_result.is_truncated = False
        mock_result.next_marker = None

        mock_bucket_obj.list_objects.return_value = mock_result
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        result = provider.list_objects("test-bucket", prefix="")

        assert len(result.objects) == 3  # 1 prefix + 2 objects
        assert result.objects[0].key == "folder1/"
        assert result.objects[0].is_directory is True
        assert result.objects[1].key == "file1.txt"
        assert result.objects[1].is_directory is False
        assert result.objects[1].size == 100
        assert result.objects[2].key == "folder2/"
        assert result.objects[2].is_directory is True

    def test_list_objects_pagination(self, provider, mock_oss2):
        """Test list_objects with pagination."""
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj

        mock_result = MagicMock()
        mock_result.prefix_list = []
        mock_result.object_list = [
            MagicMock(key="file1.txt", size=100, last_modified=1704067200, etag='"abc"'),
        ]
        mock_result.is_truncated = True
        mock_result.next_marker = "file1.txt"

        mock_bucket_obj.list_objects.return_value = mock_result
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        result = provider.list_objects("test-bucket", max_keys=1)

        assert result.is_truncated is True
        assert result.next_marker == "file1.txt"


class TestGetObject:
    """Tests for get_object method."""

    def test_get_object_returns_content(self, provider, mock_oss2):
        """Test that get_object returns file content."""
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        mock_response = MagicMock()
        mock_response.read.return_value = b"file content"
        mock_bucket_obj.get_object.return_value = mock_response

        content = provider.get_object("test-bucket", "file.txt")

        assert content == b"file content"
        mock_bucket_obj.get_object.assert_called_once_with("file.txt")


class TestPutObject:
    """Tests for put_object method."""

    def test_put_object_uploads_and_returns_metadata(self, provider, mock_oss2):
        """Test that put_object uploads data and returns metadata."""
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        mock_meta = MagicMock()
        mock_meta.content_length = 12
        mock_meta.last_modified = 1704067200
        mock_meta.etag = '"abc123"'
        mock_meta.content_type = "text/plain"
        mock_bucket_obj.head_object.return_value = mock_meta

        result = provider.put_object("test-bucket", "new-file.txt", b"file content")

        mock_bucket_obj.put_object.assert_called_once_with("new-file.txt", b"file content")
        assert result.key == "new-file.txt"
        assert result.size == 12
        assert result.etag == "abc123"
        assert result.content_type == "text/plain"


class TestDeleteObject:
    """Tests for delete_object method."""

    def test_delete_object_calls_delete(self, provider, mock_oss2):
        """Test that delete_object calls the correct method."""
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        provider.delete_object("test-bucket", "file.txt")

        mock_bucket_obj.delete_object.assert_called_once_with("file.txt")


class TestCopyObject:
    """Tests for copy_object method."""

    def test_copy_object_copies_and_returns_metadata(self, provider, mock_oss2):
        """Test that copy_object copies data and returns metadata."""
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        mock_meta = MagicMock()
        mock_meta.content_length = 100
        mock_meta.last_modified = 1704067200
        mock_meta.etag = '"def456"'
        mock_meta.content_type = "text/plain"
        mock_bucket_obj.head_object.return_value = mock_meta

        result = provider.copy_object("src-bucket", "src.txt", "dst-bucket", "dst.txt")

        mock_bucket_obj.copy_object.assert_called_once_with("src-bucket", "src.txt", "dst.txt")
        assert result.key == "dst.txt"
        assert result.size == 100


class TestExceptionHandling:
    """Tests for exception handling."""

    def test_bucket_not_found_exception(self, provider, mock_oss2):
        """Test that NoSuchBucket is converted to BucketNotFoundError."""
        import oss2.exceptions

        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.side_effect = oss2.exceptions.NoSuchBucket(
            404, {}, "", {"BucketName": "missing-bucket"}
        )

        with pytest.raises(BucketNotFoundError) as exc_info:
            provider.list_objects("missing-bucket")

        assert "missing-bucket" in str(exc_info.value)

    def test_object_not_found_exception(self, provider, mock_oss2):
        """Test that NoSuchKey is converted to ObjectNotFoundError."""
        import oss2.exceptions

        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")
        mock_bucket_obj.get_object.side_effect = oss2.exceptions.NoSuchKey(
            404, {}, "", {"Key": "missing.txt"}
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            provider.get_object("test-bucket", "missing.txt")

        assert "missing.txt" in str(exc_info.value)

    def test_access_denied_exception(self, provider, mock_oss2):
        """Test that AccessDenied is converted to PermissionDeniedError."""
        import oss2.exceptions

        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.side_effect = oss2.exceptions.AccessDenied(
            403, {}, "", {}
        )

        with pytest.raises(PermissionDeniedError):
            provider.list_objects("forbidden-bucket")

    def test_invalid_access_key_exception(self, mock_oss2):
        """Test that InvalidAccessKeyId error code is converted to AuthenticationError."""
        import oss2.exceptions

        # InvalidAccessKeyId is returned via ServerError with specific error code
        mock_oss2.BucketIterator.side_effect = oss2.exceptions.ServerError(
            403, {}, "", {"Code": "InvalidAccessKeyId", "Message": "Invalid access key"}
        )

        provider = AliyunOSSProvider(
            endpoint="oss-cn-hangzhou.aliyuncs.com",
            access_key_id="invalid-key",
            access_key_secret="secret",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            provider.list_buckets()

        assert "Invalid access key ID" in str(exc_info.value)

    def test_signature_mismatch_exception(self, mock_oss2):
        """Test that SignatureDoesNotMatch is converted to AuthenticationError."""
        import oss2.exceptions

        mock_oss2.BucketIterator.side_effect = oss2.exceptions.SignatureDoesNotMatch(
            403, {}, "", {}
        )

        provider = AliyunOSSProvider(
            endpoint="oss-cn-hangzhou.aliyuncs.com",
            access_key_id="key",
            access_key_secret="invalid-secret",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            provider.list_buckets()

        assert "Invalid access key secret" in str(exc_info.value)


class TestBucketCaching:
    """Tests for bucket caching behavior."""

    def test_bucket_is_cached(self, provider, mock_oss2):
        """Test that bucket objects are cached."""
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj
        mock_bucket_obj.get_bucket_info.return_value = MagicMock(location="cn-hangzhou")

        mock_result = MagicMock()
        mock_result.prefix_list = []
        mock_result.object_list = []
        mock_result.is_truncated = False
        mock_result.next_marker = None
        mock_bucket_obj.list_objects.return_value = mock_result

        # Call twice
        provider.list_objects("test-bucket")
        provider.list_objects("test-bucket")

        # get_bucket_info should only be called once (location is cached)
        assert mock_bucket_obj.get_bucket_info.call_count == 1

    def test_location_from_list_buckets_is_used(self, provider, mock_oss2):
        """Test that location cached from list_buckets is used."""
        # First, list buckets to cache location
        mock_bucket = MagicMock()
        mock_bucket.name = "test-bucket"
        mock_bucket.creation_date = 1704067200
        mock_bucket.location = "cn-shanghai"
        mock_oss2.BucketIterator.return_value = [mock_bucket]

        provider.list_buckets()

        # Now get bucket - should use cached location
        mock_bucket_obj = MagicMock()
        mock_oss2.Bucket.return_value = mock_bucket_obj

        mock_result = MagicMock()
        mock_result.prefix_list = []
        mock_result.object_list = []
        mock_result.is_truncated = False
        mock_result.next_marker = None
        mock_bucket_obj.list_objects.return_value = mock_result

        provider.list_objects("test-bucket")

        # Bucket should be created with the cached location endpoint
        mock_oss2.Bucket.assert_called_with(
            provider.auth,
            "https://cn-shanghai.aliyuncs.com",
            "test-bucket",
        )
