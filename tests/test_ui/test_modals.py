"""Tests for modal dialogs."""

import tempfile
from pathlib import Path

import pytest
from textual.app import App
from textual.widgets import Button, Input

from oss_tui.ui.modals.confirm import ConfirmModal
from oss_tui.ui.modals.input import InputModal
from oss_tui.ui.modals.path_input import PathInput, PathInputModal
from oss_tui.ui.modals.progress import ProgressModal


class ConfirmModalApp(App):
    """Test app for ConfirmModal."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self):
        yield ConfirmModal("Test message?")


class InputModalApp(App):
    """Test app for InputModal."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self):
        yield InputModal(
            prompt="Enter value:",
            default="default value",
            placeholder="Type something...",
        )


class TestConfirmModal:
    """Test cases for ConfirmModal."""

    @pytest.mark.asyncio
    async def test_modal_has_yes_button(self):
        """Test that modal has Yes button."""
        app = ConfirmModalApp()
        async with app.run_test() as pilot:
            yes_button = pilot.app.query_one("#yes", Button)
            assert yes_button is not None

    @pytest.mark.asyncio
    async def test_modal_has_no_button(self):
        """Test that modal has No button."""
        app = ConfirmModalApp()
        async with app.run_test() as pilot:
            no_button = pilot.app.query_one("#no", Button)
            assert no_button is not None


class TestInputModal:
    """Test cases for InputModal."""

    @pytest.mark.asyncio
    async def test_modal_has_input(self):
        """Test that modal has input field."""
        app = InputModalApp()
        async with app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            assert input_widget is not None

    @pytest.mark.asyncio
    async def test_modal_has_default_value(self):
        """Test that modal has default value."""
        app = InputModalApp()
        async with app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            assert input_widget.value == "default value"

    @pytest.mark.asyncio
    async def test_modal_has_placeholder(self):
        """Test that modal has placeholder."""
        app = InputModalApp()
        async with app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            assert input_widget.placeholder == "Type something..."


class PathInputModalApp(App):
    """Test app for PathInputModal."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def __init__(self, default: str = "", **kwargs):
        super().__init__(**kwargs)
        self._default = default

    def compose(self):
        yield PathInputModal(
            prompt="Select path:",
            default=self._default,
            placeholder="Type path...",
        )


class TestPathInputModal:
    """Test cases for PathInputModal."""

    @pytest.mark.asyncio
    async def test_modal_has_path_input(self):
        """Test that modal has path input field."""
        app = PathInputModalApp()
        async with app.run_test() as pilot:
            input_widget = pilot.app.query_one(PathInput)
            assert input_widget is not None

    @pytest.mark.asyncio
    async def test_modal_has_default_value(self):
        """Test that modal preserves default value."""
        app = PathInputModalApp(default="/tmp/test")
        async with app.run_test() as pilot:
            input_widget = pilot.app.query_one(PathInput)
            assert input_widget.value == "/tmp/test"

    @pytest.mark.asyncio
    async def test_modal_has_hint(self):
        """Test that modal shows completion hint."""
        app = PathInputModalApp()
        async with app.run_test() as pilot:
            from textual.widgets import Static

            hint = pilot.app.query_one("#path-hint", Static)
            # Check the hint widget exists
            assert hint is not None


class TestPathInput:
    """Test cases for PathInput path completion logic."""

    def test_get_completions_empty(self):
        """Test completions for empty path returns home directory contents."""
        path_input = PathInput()
        # Empty path should start from home
        completions = path_input._get_completions("")
        # Should return items from home directory
        assert isinstance(completions, list)

    def test_get_completions_directory(self):
        """Test completions for directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            Path(tmpdir, "file1.txt").touch()
            Path(tmpdir, "file2.txt").touch()
            Path(tmpdir, "subdir").mkdir()

            path_input = PathInput()
            completions = path_input._get_completions(tmpdir + "/")

            assert len(completions) == 3
            names = [p.name for p in completions]
            assert "file1.txt" in names
            assert "file2.txt" in names
            assert "subdir" in names

    def test_get_completions_partial_match(self):
        """Test completions for partial filename match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            Path(tmpdir, "apple.txt").touch()
            Path(tmpdir, "apricot.txt").touch()
            Path(tmpdir, "banana.txt").touch()

            path_input = PathInput()
            completions = path_input._get_completions(tmpdir + "/ap")

            assert len(completions) == 2
            names = [p.name for p in completions]
            assert "apple.txt" in names
            assert "apricot.txt" in names
            assert "banana.txt" not in names

    def test_get_completions_nonexistent_directory(self):
        """Test completions for nonexistent directory."""
        path_input = PathInput()
        completions = path_input._get_completions("/nonexistent/path/")
        assert completions == []

    def test_format_path_file(self):
        """Test format_path for regular file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir, "test.txt")
            file_path.touch()

            path_input = PathInput()
            formatted = path_input._format_path(file_path)
            assert not formatted.endswith("/")

    def test_format_path_directory(self):
        """Test format_path adds trailing slash for directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir, "subdir")
            dir_path.mkdir()

            path_input = PathInput()
            formatted = path_input._format_path(dir_path)
            assert formatted.endswith("/")


class ProgressModalApp(App):
    """Test app for ProgressModal."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def __init__(self, total_files: int = 10, total_bytes: int = 1024, **kwargs):
        super().__init__(**kwargs)
        self._total_files = total_files
        self._total_bytes = total_bytes

    def compose(self):
        yield ProgressModal(
            title="Test Transfer",
            total_files=self._total_files,
            total_bytes=self._total_bytes,
        )


class TestProgressModal:
    """Test cases for ProgressModal."""

    @pytest.mark.asyncio
    async def test_modal_has_progress_bar(self):
        """Test that modal has progress bar."""
        from textual.widgets import ProgressBar

        app = ProgressModalApp()
        async with app.run_test() as pilot:
            progress_bar = pilot.app.query_one("#progress", ProgressBar)
            assert progress_bar is not None

    @pytest.mark.asyncio
    async def test_modal_has_title(self):
        """Test that modal has title."""
        from textual.widgets import Label

        app = ProgressModalApp()
        async with app.run_test() as pilot:
            title = pilot.app.query_one("#title", Label)
            assert title is not None

    @pytest.mark.asyncio
    async def test_modal_update_progress(self):
        """Test that progress can be updated."""
        app = ProgressModalApp(total_files=10, total_bytes=10240)
        async with app.run_test() as pilot:
            modal = pilot.app.query_one(ProgressModal)
            modal.update_progress(5, 5120, "test_file.txt")
            await pilot.pause()

            # Verify internal state is updated
            assert modal._completed_files == 5
            assert modal._transferred_bytes == 5120
            assert modal._current_file == "test_file.txt"

    @pytest.mark.asyncio
    async def test_modal_cancelled_state(self):
        """Test that modal tracks cancelled state."""
        app = ProgressModalApp()
        async with app.run_test() as pilot:
            modal = pilot.app.query_one(ProgressModal)
            assert modal.is_cancelled is False

    def test_format_size_bytes(self):
        """Test size formatting for bytes."""
        assert ProgressModal._format_size(512) == "512.0 B"

    def test_format_size_kilobytes(self):
        """Test size formatting for kilobytes."""
        assert ProgressModal._format_size(2048) == "2.0 KB"

    def test_format_size_megabytes(self):
        """Test size formatting for megabytes."""
        assert ProgressModal._format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_format_size_gigabytes(self):
        """Test size formatting for gigabytes."""
        assert ProgressModal._format_size(2 * 1024 * 1024 * 1024) == "2.0 GB"
