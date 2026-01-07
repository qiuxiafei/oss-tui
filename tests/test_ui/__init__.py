"""Tests for FileList widget."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from textual.app import App
from textual.pilot import Pilot

from oss_tui.models.object import Object
from oss_tui.ui.widgets.file_list import FileList, FileListItem


class FileListApp(App):
    """Test app for FileList widget."""

    def compose(self):
        yield FileList(id="file-list")


class TestFileListItem:
    """Test cases for FileListItem."""

    def test_file_item_display(self):
        """Test that file item displays correctly."""
        obj = Object(
            key="test.txt",
            size=1024,
            last_modified=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        )
        item = FileListItem(obj)

        # Check that the item has the object
        assert item.obj == obj

    def test_directory_item_display(self):
        """Test that directory item displays correctly."""
        obj = Object(
            key="subdir/",
            size=0,
            is_directory=True,
        )
        item = FileListItem(obj)

        assert item.obj == obj
        assert item.obj.is_directory is True


class TestFileList:
    """Test cases for FileList widget."""

    @pytest.fixture
    def app(self):
        return FileListApp()

    @pytest.fixture
    def pilot(self, app):
        return app.run_test()

    def test_load_objects(self, pilot: Pilot):
        """Test loading objects into the file list."""
        file_list = pilot.app.query_one("#file-list", FileList)

        objects = [
            Object(key="file1.txt", size=100),
            Object(key="file2.txt", size=200),
        ]

        file_list.load_objects(objects, path="test/")

        assert file_list.current_path == "test/"
        assert len(file_list._objects) == 2

    def test_clear_all(self, pilot: Pilot):
        """Test clearing all objects."""
        file_list = pilot.app.query_one("#file-list", FileList)

        objects = [Object(key="test.txt", size=100)]
        file_list.load_objects(objects)
        file_list.clear_all()

        assert len(file_list._objects) == 0
        assert file_list.current_path == ""

    def test_apply_filter(self, pilot: Pilot):
        """Test applying filter to objects."""
        file_list = pilot.app.query_one("#file-list", FileList)

        objects = [
            Object(key="test1.txt", size=100),
            Object(key="test2.txt", size=200),
            Object(key="other.txt", size=300),
        ]

        file_list.load_objects(objects)
        file_list.apply_filter("test")

        assert len(file_list._filtered_objects) == 2

    def test_clear_filter(self, pilot: Pilot):
        """Test clearing filter."""
        file_list = pilot.app.query_one("#file-list", FileList)

        objects = [
            Object(key="test1.txt", size=100),
            Object(key="other.txt", size=300),
        ]

        file_list.load_objects(objects)
        file_list.apply_filter("test")
        file_list.clear_filter()

        assert len(file_list._filtered_objects) == 2
        assert file_list._filter_query == ""

    def test_action_go_top(self, pilot: Pilot):
        """Test going to top of list."""
        file_list = pilot.app.query_one("#file-list", FileList)

        objects = [
            Object(key=f"file{i}.txt", size=100) for i in range(10)
        ]
        file_list.load_objects(objects)

        # Move to bottom first
        file_list.index = 9

        # Go to top
        file_list.action_go_top()

        assert file_list.index == 0

    def test_action_go_bottom(self, pilot: Pilot):
        """Test going to bottom of list."""
        file_list = pilot.app.query_one("#file-list", FileList)

        objects = [
            Object(key=f"file{i}.txt", size=100) for i in range(10)
        ]
        file_list.load_objects(objects)

        # Go to bottom
        file_list.action_go_bottom()

        assert file_list.index == 9

    def test_current_path_property(self, pilot: Pilot):
        """Test current_path property."""
        file_list = pilot.app.query_one("#file-list", FileList)

        assert file_list.current_path == ""

        file_list.load_objects([], path="test/path/")
        assert file_list.current_path == "test/path/"
