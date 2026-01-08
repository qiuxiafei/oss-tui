"""Progress modal dialog for directory transfers."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ProgressBar, Static


class ProgressModal(ModalScreen[bool]):
    """A modal dialog showing transfer progress.

    Returns True if completed successfully, False if cancelled.
    """

    CSS = """
    ProgressModal {
        align: center middle;
    }

    ProgressModal > Vertical {
        width: 70;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
    }

    ProgressModal #title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    ProgressModal #status {
        width: 100%;
        margin-bottom: 1;
    }

    ProgressModal #current-file {
        width: 100%;
        color: $text-muted;
        margin-bottom: 1;
    }

    ProgressModal ProgressBar {
        width: 100%;
        margin-bottom: 1;
    }

    ProgressModal #hint {
        width: 100%;
        text-align: center;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(
        self,
        title: str = "Transferring...",
        total_files: int = 0,
        total_bytes: int = 0,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the progress modal.

        Args:
            title: The title to display.
            total_files: Total number of files to transfer.
            total_bytes: Total bytes to transfer.
        """
        super().__init__(*args, **kwargs)
        self._title = title
        self._total_files = total_files
        self._total_bytes = total_bytes
        self._completed_files = 0
        self._transferred_bytes = 0
        self._current_file = ""
        self._cancelled = False

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical():
            yield Label(self._title, id="title")
            yield Static("Preparing...", id="status")
            yield Static("", id="current-file")
            yield ProgressBar(total=100, id="progress")
            yield Static("Press [Esc] to cancel", id="hint")

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_display()

    def update_progress(
        self,
        completed_files: int,
        transferred_bytes: int,
        current_file: str = "",
    ) -> None:
        """Update the progress display.

        Args:
            completed_files: Number of files completed.
            transferred_bytes: Bytes transferred so far.
            current_file: Name of the file currently being transferred.
        """
        self._completed_files = completed_files
        self._transferred_bytes = transferred_bytes
        self._current_file = current_file
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with current progress."""
        # Update status text
        status = self.query_one("#status", Static)
        if self._total_files > 0:
            percent = (self._completed_files / self._total_files) * 100
            size_info = self._format_size_progress()
            status.update(
                f"Files: {self._completed_files}/{self._total_files} "
                f"({percent:.1f}%) {size_info}"
            )
        else:
            status.update("Calculating...")

        # Update current file
        current_file_widget = self.query_one("#current-file", Static)
        if self._current_file:
            # Truncate long file names
            display_name = self._current_file
            if len(display_name) > 60:
                display_name = "..." + display_name[-57:]
            current_file_widget.update(f"Current: {display_name}")
        else:
            current_file_widget.update("")

        # Update progress bar
        progress_bar = self.query_one("#progress", ProgressBar)
        if self._total_files > 0:
            progress_bar.progress = (self._completed_files / self._total_files) * 100
        else:
            progress_bar.progress = 0

    def _format_size_progress(self) -> str:
        """Format the size progress string."""
        if self._total_bytes == 0:
            return ""

        transferred = self._format_size(self._transferred_bytes)
        total = self._format_size(self._total_bytes)
        return f"| {transferred} / {total}"

    @staticmethod
    def _format_size(size: int) -> str:
        """Format size in human-readable format."""
        size_float = float(size)
        for unit in ["B", "KB", "MB", "GB"]:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024
        return f"{size_float:.1f} TB"

    def complete(self) -> None:
        """Mark the transfer as complete and close the modal."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel the transfer."""
        self._cancelled = True
        self.dismiss(False)

    @property
    def is_cancelled(self) -> bool:
        """Check if the transfer was cancelled."""
        return self._cancelled
