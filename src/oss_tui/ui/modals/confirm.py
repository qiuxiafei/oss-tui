"""Confirmation modal dialog."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmModal(ModalScreen[bool]):
    """A modal dialog for confirming actions."""

    CSS = """
    ConfirmModal {
        align: center middle;
    }

    ConfirmModal > Vertical {
        width: 50;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }

    ConfirmModal Label {
        width: 100%;
        margin-bottom: 1;
        text-align: center;
    }

    ConfirmModal Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
    }

    ConfirmModal Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "cancel", "No", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(self, message: str, *args, **kwargs) -> None:
        """Initialize the confirmation modal.

        Args:
            message: The confirmation message to display.
        """
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical():
            yield Label(self.message)
            with Horizontal():
                yield Button("Yes (y)", id="yes", variant="error")
                yield Button("No (n)", id="no", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss(event.button.id == "yes")

    def action_confirm(self) -> None:
        """Confirm the action."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel the action."""
        self.dismiss(False)
