"""File list widget."""

from textual.widgets import ListView


class FileList(ListView):
    """Widget displaying a list of files and directories.

    Supports Vim-style navigation and file operations.
    """

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("g", "go_top", "Top"),
        ("G", "go_bottom", "Bottom"),
        ("l", "select_cursor", "Enter"),
        ("h", "go_back", "Back"),
    ]

    def action_go_top(self) -> None:
        """Go to the first item."""
        self.index = 0

    def action_go_bottom(self) -> None:
        """Go to the last item."""
        if self._nodes:
            self.index = len(self._nodes) - 1

    def action_go_back(self) -> None:
        """Go back to parent directory."""
        # TODO: Implement navigation to parent
        pass
