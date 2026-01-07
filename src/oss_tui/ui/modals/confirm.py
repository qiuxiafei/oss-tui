"""Confirmation modal dialog."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmModal(ModalScreen[bool]):
    """A modal dialog for confirming actions."""

    def __init__(self, message: str, *args, **kwargs) -> None:
        """Initialize the confirmation modal.

        Args:
            message: The confirmation message to display.
        """
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        yield Label(self.message)
        with Horizontal():
            yield Button("Yes", id="yes", variant="primary")
            yield Button("No", id="no", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss(event.button.id == "yes")
