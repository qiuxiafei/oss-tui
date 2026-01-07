"""Tests for modal dialogs."""

import pytest
from textual.app import App
from textual.widgets import Button, Input

from oss_tui.ui.modals.confirm import ConfirmModal
from oss_tui.ui.modals.input import InputModal


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
