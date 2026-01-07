"""Bucket list widget."""

from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from oss_tui.models.bucket import Bucket


class BucketListItem(ListItem):
    """A list item representing a bucket."""

    def __init__(self, bucket: Bucket) -> None:
        """Initialize the bucket list item.

        Args:
            bucket: The bucket to display.
        """
        super().__init__()
        self.bucket = bucket

    def compose(self):
        """Compose the list item."""
        yield Static(f"  {self.bucket.name}")


class BucketList(ListView):
    """Widget displaying a list of buckets.

    Supports Vim-style navigation (j/k).
    """

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("g", "go_top", "Top"),
        ("G", "go_bottom", "Bottom"),
        ("l", "select_cursor", "Enter"),
        ("enter", "select_cursor", "Enter"),
        ("home", "go_top", "Top"),
        ("end", "go_bottom", "Bottom"),
    ]

    class BucketSelected(Message):
        """Message sent when a bucket is selected."""

        def __init__(self, bucket: Bucket) -> None:
            """Initialize the message.

            Args:
                bucket: The selected bucket.
            """
            super().__init__()
            self.bucket = bucket

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the bucket list."""
        super().__init__(*args, **kwargs)
        self._buckets: list[Bucket] = []

    def load_buckets(self, buckets: list[Bucket]) -> None:
        """Load buckets into the list.

        Args:
            buckets: List of buckets to display.
        """
        self._buckets = buckets
        self.clear()
        for bucket in buckets:
            self.append(BucketListItem(bucket))

    def action_go_top(self) -> None:
        """Go to the first item."""
        self.index = 0

    def action_go_bottom(self) -> None:
        """Go to the last item."""
        if self._nodes:
            self.index = len(self._nodes) - 1

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle item selection."""
        if isinstance(event.item, BucketListItem):
            self.post_message(self.BucketSelected(event.item.bucket))
