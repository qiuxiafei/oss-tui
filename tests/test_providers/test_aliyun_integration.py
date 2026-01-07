"""Integration tests for AliyunOSSProvider using real OSS credentials.

These tests require valid OSS credentials set in environment variables:
- OSS_ENDPOINT: OSS endpoint (e.g., oss-cn-hangzhou.aliyuncs.com)
- OSS_ACCESS_KEY_ID: Access key ID
- OSS_ACCESS_KEY_SECRET: Access key secret

Tests will be skipped if credentials are not configured.
"""

import os
import uuid
from datetime import datetime

import pytest

from oss_tui.providers.aliyun import AliyunOSSProvider

# Skip all tests if credentials not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("OSS_ACCESS_KEY_ID") or not os.getenv("OSS_ACCESS_KEY_SECRET"),
    reason="OSS credentials not configured (set OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET)",
)


@pytest.fixture
def provider():
    """Create a provider with real credentials."""
    return AliyunOSSProvider(
        endpoint=os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com"),
        access_key_id=os.getenv("OSS_ACCESS_KEY_ID", ""),
        access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET", ""),
    )


@pytest.fixture
def test_bucket(provider):
    """Get a test bucket name from the first available bucket.

    In integration tests, we use an existing bucket rather than creating one,
    as bucket creation/deletion is a sensitive operation.
    """
    buckets = provider.list_buckets()
    if not buckets:
        pytest.skip("No buckets available for testing")
    return buckets[0].name


@pytest.fixture
def test_object_key():
    """Generate a unique object key for testing."""
    return f"oss-tui-test/{uuid.uuid4().hex[:8]}/test-file.txt"


class TestListBucketsIntegration:
    """Integration tests for list_buckets."""

    def test_list_buckets_returns_buckets(self, provider):
        """Test that we can list buckets from real OSS."""
        buckets = provider.list_buckets()

        assert isinstance(buckets, list)
        # Should have at least one bucket for meaningful test
        if len(buckets) > 0:
            bucket = buckets[0]
            assert bucket.name
            assert bucket.location
            assert isinstance(bucket.creation_date, datetime)


class TestListObjectsIntegration:
    """Integration tests for list_objects."""

    def test_list_objects_returns_result(self, provider, test_bucket):
        """Test that we can list objects from a real bucket."""
        result = provider.list_objects(test_bucket, prefix="", max_keys=10)

        assert hasattr(result, "objects")
        assert hasattr(result, "is_truncated")
        assert isinstance(result.objects, list)


class TestObjectOperationsIntegration:
    """Integration tests for object CRUD operations."""

    def test_put_get_delete_object(self, provider, test_bucket, test_object_key):
        """Test full lifecycle: put, get, delete object."""
        test_content = b"Hello, OSS-TUI integration test!"

        try:
            # Put object
            put_result = provider.put_object(test_bucket, test_object_key, test_content)
            assert put_result.key == test_object_key
            assert put_result.size == len(test_content)

            # Get object
            content = provider.get_object(test_bucket, test_object_key)
            assert content == test_content

            # List to verify
            result = provider.list_objects(
                test_bucket,
                prefix=test_object_key,
            )
            keys = [obj.key for obj in result.objects]
            assert test_object_key in keys

        finally:
            # Clean up - delete the test object
            try:
                provider.delete_object(test_bucket, test_object_key)
            except Exception:
                pass  # Ignore cleanup errors

    def test_copy_object(self, provider, test_bucket, test_object_key):
        """Test copying an object."""
        test_content = b"Content to be copied"
        copy_key = test_object_key.replace("test-file.txt", "test-file-copy.txt")

        try:
            # Create source object
            provider.put_object(test_bucket, test_object_key, test_content)

            # Copy object
            copy_result = provider.copy_object(
                test_bucket, test_object_key, test_bucket, copy_key
            )
            assert copy_result.key == copy_key
            assert copy_result.size == len(test_content)

            # Verify copy content
            content = provider.get_object(test_bucket, copy_key)
            assert content == test_content

        finally:
            # Clean up
            for key in [test_object_key, copy_key]:
                try:
                    provider.delete_object(test_bucket, key)
                except Exception:
                    pass


class TestCrossRegionIntegration:
    """Integration tests for cross-region bucket access."""

    def test_bucket_location_caching(self, provider):
        """Test that bucket locations are cached after list_buckets."""
        buckets = provider.list_buckets()

        if not buckets:
            pytest.skip("No buckets available")

        # All listed buckets should have their location cached
        for bucket in buckets:
            assert bucket.name in provider._bucket_locations
            assert provider._bucket_locations[bucket.name] == bucket.location
