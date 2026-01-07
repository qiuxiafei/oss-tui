"""Status bar widget."""

from textual.widgets import Static


class StatusBar(Static):
    """Widget displaying status information and key hints."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the status bar."""
        super().__init__(*args, **kwargs)
        self.update_hints()

    def update_hints(self, hints: str | None = None) -> None:
        """Update the displayed key hints.

        Args:
            hints: Key hints to display. Uses default if not provided.
        """
        if hints is None:
            hints = "[j/k] Navigate  [l] Enter  [h] Back  [/] Search  [?] Help"
        self.update(hints)
