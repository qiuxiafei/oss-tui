"""Search input widget for filtering lists."""

from textual.message import Message
from textual.widgets import Input


class SearchInput(Input):
    """A search input widget that appears at the bottom of the screen.

    Used for filtering bucket and file lists with Vim-style `/` activation.
    """

    class SearchSubmitted(Message):
        """Message sent when search is submitted (Enter pressed)."""

        def __init__(self, query: str) -> None:
            """Initialize the message.

            Args:
                query: The search query string.
            """
            super().__init__()
            self.query = query

    class SearchChanged(Message):
        """Message sent when search text changes (for live filtering)."""

        def __init__(self, query: str) -> None:
            """Initialize the message.

            Args:
                query: The current search query string.
            """
            super().__init__()
            self.query = query

    class SearchCancelled(Message):
        """Message sent when search is cancelled (ESC pressed)."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the search input."""
        kwargs.setdefault("placeholder", "Search...")
        super().__init__(*args, **kwargs)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for live filtering."""
        self.post_message(self.SearchChanged(event.value))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission."""
        self.post_message(self.SearchSubmitted(event.value))

    def key_escape(self) -> None:
        """Handle ESC key to cancel search."""
        self.post_message(self.SearchCancelled())
