"""Main Textual application for OSS-TUI."""

from textual.app import App
from textual.binding import Binding


class OssTuiApp(App):
    """The main OSS-TUI application."""

    TITLE = "OSS-TUI"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("a", "switch_account", "Switch Account"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self):
        """Compose the application layout."""
        # TODO: Implement the main layout with bucket list and file list
        from textual.widgets import Footer, Header

        yield Header()
        yield Footer()

    def action_help(self) -> None:
        """Show help modal."""
        # TODO: Implement help modal
        pass

    def action_switch_account(self) -> None:
        """Switch to a different account."""
        # TODO: Implement account switching
        pass

    def action_refresh(self) -> None:
        """Refresh the current view."""
        # TODO: Implement refresh
        pass
