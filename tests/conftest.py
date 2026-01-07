"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_filesystem(temp_dir: Path):
    """Create a sample filesystem structure for testing.

    Structure:
        temp_dir/
        ├── bucket1/
        │   ├── file1.txt
        │   ├── file2.txt
        │   └── subdir/
        │       └── file3.txt
        └── bucket2/
            └── data.json
    """
    # Create bucket1
    bucket1 = temp_dir / "bucket1"
    bucket1.mkdir()
    (bucket1 / "file1.txt").write_text("content1")
    (bucket1 / "file2.txt").write_text("content2")

    subdir = bucket1 / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("content3")

    # Create bucket2
    bucket2 = temp_dir / "bucket2"
    bucket2.mkdir()
    (bucket2 / "data.json").write_text('{"key": "value"}')

    return temp_dir
