"""Main screen for OSS-TUI."""

from textual.screen import Screen
from textual.widgets import Static


class MainScreen(Screen):
    """The main application screen with bucket and file lists."""

    def compose(self):
        """Compose the main screen layout."""
        # TODO: Implement dual-pane layout
        yield Static("OSS-TUI Main Screen - TODO")
