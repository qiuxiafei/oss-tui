"""Bucket list widget."""

from textual.widgets import ListView


class BucketList(ListView):
    """Widget displaying a list of buckets.

    Supports Vim-style navigation (j/k).
    """

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("g", "go_top", "Top"),
        ("G", "go_bottom", "Bottom"),
    ]

    def action_go_top(self) -> None:
        """Go to the first item."""
        self.index = 0

    def action_go_bottom(self) -> None:
        """Go to the last item."""
        if self._nodes:
            self.index = len(self._nodes) - 1
