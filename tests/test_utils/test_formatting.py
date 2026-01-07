"""Tests for formatting utilities."""

from datetime import datetime, timezone

import pytest

from oss_tui.utils.formatting import format_size, format_time


class TestFormatSize:
    """Test cases for format_size function."""

    def test_bytes(self):
        """Test formatting bytes."""
        assert format_size(0) == "0 B"
        assert format_size(500) == "500 B"
        assert format_size(1023) == "1023 B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(1536) == "1.5 KB"
        # 1024 * 1024 - 1 = 1048575 bytes = 1023.9 KB would round to 1024.0 KB
        assert format_size(1024 * 1024 - 1) == "1024.0 KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(int(1024 * 1024 * 5.5)) == "5.5 MB"
        # 1024^3 - 1 bytes rounds to 1024.0 MB
        assert format_size(1024 * 1024 * 1024 - 1) == "1024.0 MB"

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_size(int(1024 * 1024 * 1024 * 2.5)) == "2.5 GB"


class TestFormatTime:
    """Test cases for format_time function."""

    def test_none_datetime(self):
        """Test formatting None datetime."""
        assert format_time(None) == ""
        assert format_time(None, include_time=True) == ""

    def test_date_only(self):
        """Test formatting date only."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert format_time(dt) == "2024-01-15"

    def test_with_time(self):
        """Test formatting with time."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert format_time(dt, include_time=True) == "2024-01-15 10:30"

    def test_different_dates(self):
        """Test formatting different dates."""
        dt1 = datetime(2023, 12, 31, 23, 59, tzinfo=timezone.utc)
        dt2 = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)

        assert format_time(dt1) == "2023-12-31"
        assert format_time(dt2) == "2025-01-01"
