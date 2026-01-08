"""Path input modal dialog with path completion support."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static


class PathInput(Input):
    """Input widget with path completion support."""

    BINDINGS = [
        Binding("tab", "complete", "Complete", show=False),
    ]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the path input."""
        super().__init__(*args, **kwargs)
        self._completions: list[Path] = []
        self._completion_index: int = 0
        self._last_completed_text: str = ""

    def _get_completions(self, path_text: str) -> list[Path]:
        """Get path completions for the given text.

        Args:
            path_text: The current path text to complete.

        Returns:
            List of matching paths.
        """
        if not path_text:
            # Start from home directory
            path_text = str(Path.home()) + "/"

        # Expand user home directory (~)
        expanded = Path(path_text).expanduser()

        # If the path ends with a separator, list directory contents
        if path_text.endswith("/") or path_text.endswith("\\"):
            if expanded.is_dir():
                try:
                    return sorted(expanded.iterdir())
                except PermissionError:
                    return []
            return []

        # Otherwise, find matching entries in parent directory
        parent = expanded.parent
        partial_name = expanded.name

        if not parent.exists():
            return []

        try:
            matches = [
                p
                for p in sorted(parent.iterdir())
                if p.name.lower().startswith(partial_name.lower())
            ]
            return matches
        except PermissionError:
            return []

    def _format_path(self, path: Path) -> str:
        """Format a path for display, adding trailing slash for directories.

        Args:
            path: The path to format.

        Returns:
            Formatted path string.
        """
        result = str(path)
        if path.is_dir() and not result.endswith("/"):
            result += "/"
        return result

    def action_complete(self) -> None:
        """Handle tab completion."""
        current_text = self.value
        hint_widget = self.screen.query_one("#path-hint", Static)

        # Check if we're cycling through existing completions
        if (
            self._completions
            and current_text == self._last_completed_text
            and len(self._completions) > 1
        ):
            # Cycle to next completion
            self._completion_index = (self._completion_index + 1) % len(
                self._completions
            )
            completed_path = self._format_path(
                self._completions[self._completion_index]
            )
            self.value = completed_path
            self._last_completed_text = completed_path
            self.cursor_position = len(completed_path)

            # Update hint
            hint_widget.update(
                f"({self._completion_index + 1}/{len(self._completions)}) "
                f"Tab: cycle, Enter: confirm"
            )
            return

        # Get new completions
        self._completions = self._get_completions(current_text)
        self._completion_index = 0

        if not self._completions:
            hint_widget.update("No matches found")
            return

        if len(self._completions) == 1:
            # Single match - complete it
            completed_path = self._format_path(self._completions[0])
            self.value = completed_path
            self._last_completed_text = completed_path
            self.cursor_position = len(completed_path)
            hint_widget.update("Tab: complete, Enter: confirm")
        else:
            # Multiple matches - complete to common prefix and show options
            completed_path = self._format_path(self._completions[0])
            self.value = completed_path
            self._last_completed_text = completed_path
            self.cursor_position = len(completed_path)

            # Show hint about multiple matches
            hint_widget.update(
                f"(1/{len(self._completions)}) Tab: cycle, Enter: confirm"
            )


class PathInputModal(ModalScreen[str | None]):
    """A modal dialog for path input with completion support."""

    CSS = """
    PathInputModal {
        align: center middle;
    }

    PathInputModal > Vertical {
        width: 70;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }

    PathInputModal Label {
        width: 100%;
        margin-bottom: 1;
    }

    PathInputModal PathInput {
        width: 100%;
    }

    PathInputModal #path-hint {
        width: 100%;
        height: 1;
        margin-top: 1;
        color: $text-muted;
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
        """Initialize the path input modal.

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
            yield PathInput(
                value=self.default,
                placeholder=self.placeholder,
                id="path-input",
            )
            yield Static("Tab: complete path, Enter: confirm", id="path-hint")

    def on_mount(self) -> None:
        """Focus the input field on mount."""
        path_input = self.query_one("#path-input", PathInput)
        path_input.focus()
        # Place cursor at end of text
        path_input.cursor_position = len(path_input.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        """Cancel the input modal."""
        self.dismiss(None)
