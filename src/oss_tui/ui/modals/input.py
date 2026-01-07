"""Input modal dialog for getting user input."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class InputModal(ModalScreen[str | None]):
    """A modal dialog for getting text input from the user."""

    CSS = """
    InputModal {
        align: center middle;
    }

    InputModal > Vertical {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }

    InputModal Label {
        width: 100%;
        margin-bottom: 1;
    }

    InputModal Input {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(
        self,
        prompt: str,
        default: str = "",
        placeholder: str = "",
        *args,
        **kwargs,
    ) -> None:
        """Initialize the input modal.

        Args:
            prompt: The prompt message to display.
            default: Default value for the input.
            placeholder: Placeholder text for the input.
        """
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.default = default
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical():
            yield Label(self.prompt)
            yield Input(
                value=self.default,
                placeholder=self.placeholder,
                id="input-field",
            )

    def on_mount(self) -> None:
        """Focus the input field on mount."""
        self.query_one("#input-field", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        """Cancel the input modal."""
        self.dismiss(None)
