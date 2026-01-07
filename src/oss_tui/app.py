"""Main Textual application for OSS-TUI."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from oss_tui.providers.filesystem import FilesystemProvider
from oss_tui.ui.widgets.bucket_list import BucketList
from oss_tui.ui.widgets.file_list import FileList


class OssTuiApp(App):
    """The main OSS-TUI application."""

    TITLE = "OSS-TUI"

    CSS = """
    #main-container {
        layout: horizontal;
    }

    #left-pane {
        width: 30%;
        min-width: 20;
        border: solid $primary;
    }

    #right-pane {
        width: 70%;
        border: solid $secondary;
    }

    #bucket-header, #file-header {
        height: 3;
        background: $surface;
        padding: 1;
        text-style: bold;
    }

    #bucket-list {
        height: 1fr;
    }

    #file-list {
        height: 1fr;
    }

    #path-bar {
        height: 1;
        background: $surface-darken-1;
        padding: 0 1;
    }

    BucketList > ListItem {
        padding: 0 1;
    }

    FileList > ListItem {
        padding: 0 1;
    }

    BucketList > ListItem.--highlight {
        background: $accent;
    }

    FileList > ListItem.--highlight {
        background: $accent;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("r", "refresh", "Refresh"),
        Binding("tab", "switch_pane", "Switch Pane"),
    ]

    def __init__(self, root: str | None = None) -> None:
        """Initialize the application.

        Args:
            root: Root directory for FilesystemProvider. Defaults to home.
        """
        super().__init__()
        self.provider = FilesystemProvider(root=root)
        self._current_bucket: str | None = None
        self._current_path: str = ""

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="left-pane"):
                yield Static("Buckets", id="bucket-header")
                yield BucketList(id="bucket-list")
            with Vertical(id="right-pane"):
                yield Static("Files", id="file-header")
                yield Static("", id="path-bar")
                yield FileList(id="file-list")
        yield Footer()

    def on_mount(self) -> None:
        """Handle application mount."""
        self._load_buckets()
        # Focus the bucket list initially
        self.query_one("#bucket-list", BucketList).focus()

    def _load_buckets(self) -> None:
        """Load buckets into the bucket list."""
        try:
            buckets = self.provider.list_buckets()
            bucket_list = self.query_one("#bucket-list", BucketList)
            bucket_list.load_buckets(buckets)

            # Update header with count
            header = self.query_one("#bucket-header", Static)
            header.update(f"Buckets ({len(buckets)})")
        except Exception as e:
            self.notify(f"Error loading buckets: {e}", severity="error")

    def _load_objects(self, bucket: str, prefix: str = "") -> None:
        """Load objects into the file list.

        Args:
            bucket: The bucket name.
            prefix: The prefix/path to list.
        """
        try:
            result = self.provider.list_objects(bucket, prefix=prefix)
            file_list = self.query_one("#file-list", FileList)
            file_list.load_objects(result.objects, prefix)

            # Update path bar
            path_bar = self.query_one("#path-bar", Static)
            path_display = f"/{bucket}/{prefix}" if prefix else f"/{bucket}/"
            path_bar.update(path_display)

            # Update header
            header = self.query_one("#file-header", Static)
            header.update(f"Files ({len(result.objects)})")

            self._current_bucket = bucket
            self._current_path = prefix
        except Exception as e:
            self.notify(f"Error loading objects: {e}", severity="error")

    def on_bucket_list_bucket_selected(
        self, event: BucketList.BucketSelected
    ) -> None:
        """Handle bucket selection."""
        self._load_objects(event.bucket.name)
        # Focus the file list
        self.query_one("#file-list", FileList).focus()

    def on_file_list_directory_entered(
        self, event: FileList.DirectoryEntered
    ) -> None:
        """Handle entering a directory."""
        if self._current_bucket:
            self._load_objects(self._current_bucket, event.path)

    def on_file_list_go_back(self, event: FileList.GoBack) -> None:
        """Handle going back to parent directory."""
        if not self._current_bucket:
            return

        if self._current_path:
            # Go up one directory level
            parts = self._current_path.rstrip("/").split("/")
            if len(parts) > 1:
                new_path = "/".join(parts[:-1]) + "/"
                self._load_objects(self._current_bucket, new_path)
            else:
                # At root of bucket
                self._load_objects(self._current_bucket, "")
        else:
            # At bucket root, focus bucket list
            self.query_one("#bucket-list", BucketList).focus()

    def action_help(self) -> None:
        """Show help modal."""
        self.notify(
            "[j/k] Navigate  [l/Enter] Enter  [h/Bksp] Back  [Tab] Switch  [q] Quit",
            title="Help",
        )

    def action_refresh(self) -> None:
        """Refresh the current view."""
        self._load_buckets()
        if self._current_bucket:
            self._load_objects(self._current_bucket, self._current_path)
        self.notify("Refreshed", severity="information")

    def action_switch_pane(self) -> None:
        """Switch focus between panes."""
        bucket_list = self.query_one("#bucket-list", BucketList)
        file_list = self.query_one("#file-list", FileList)

        if bucket_list.has_focus:
            file_list.focus()
        else:
            bucket_list.focus()
