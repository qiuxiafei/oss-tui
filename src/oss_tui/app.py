"""Main Textual application for OSS-TUI."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from oss_tui.config.loader import get_account_config, get_account_names, load_config
from oss_tui.config.settings import AppConfig
from oss_tui.providers import create_provider
from oss_tui.providers.factory import OSSProviderProtocol
from oss_tui.ui.modals.confirm import ConfirmModal
from oss_tui.ui.modals.input import InputModal
from oss_tui.ui.modals.preview import MAX_PREVIEW_SIZE, PreviewModal
from oss_tui.ui.widgets.bucket_list import BucketList
from oss_tui.ui.widgets.file_list import FileList
from oss_tui.ui.widgets.search_input import SearchInput

# Default download directory
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads"


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

    #search-container {
        height: auto;
        display: none;
    }

    #search-container.visible {
        display: block;
    }

    #search-input {
        height: 3;
        background: $surface;
        border: solid $primary;
    }

    BucketList > ListItem {
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
        Binding("slash", "start_search", "Search"),
        Binding("escape", "cancel_search", "Cancel", show=False),
        Binding("a", "switch_account", "Account"),
    ]

    def __init__(
        self,
        config: AppConfig | None = None,
        account: str | None = None,
    ) -> None:
        """Initialize the application.

        Args:
            config: Application configuration. If not provided, loads from file.
            account: Account name to use. If not provided, uses default from config.
        """
        super().__init__()

        # Load configuration
        self._config = config or load_config()

        # Get account configuration
        self._account_name, account_config = get_account_config(
            self._config, account
        )

        # Create provider from configuration
        self.provider: OSSProviderProtocol = create_provider(account_config)

        self._current_bucket: str | None = None
        self._current_path: str = ""
        self._search_active: bool = False
        self._last_focused_widget: str = "#bucket-list"

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
        with Vertical(id="search-container"):
            yield SearchInput(id="search-input")
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

    def action_start_search(self) -> None:
        """Start search mode."""
        if self._search_active:
            return

        # Remember which widget was focused
        bucket_list = self.query_one("#bucket-list", BucketList)
        file_list = self.query_one("#file-list", FileList)
        if bucket_list.has_focus:
            self._last_focused_widget = "#bucket-list"
        elif file_list.has_focus:
            self._last_focused_widget = "#file-list"

        self._search_active = True
        search_container = self.query_one("#search-container")
        search_container.add_class("visible")

        search_input = self.query_one("#search-input", SearchInput)
        search_input.value = ""
        search_input.focus()

    def action_cancel_search(self) -> None:
        """Cancel search mode and clear filter."""
        if not self._search_active:
            return

        self._search_active = False
        search_container = self.query_one("#search-container")
        search_container.remove_class("visible")

        # Clear filters
        self.query_one("#bucket-list", BucketList).clear_filter()
        self.query_one("#file-list", FileList).clear_filter()

        # Restore focus to the previously focused widget
        self.query_one(self._last_focused_widget).focus()

    def on_search_input_search_changed(
        self, event: SearchInput.SearchChanged
    ) -> None:
        """Handle live search filtering."""
        query = event.query.lower()

        # Filter the active list based on which was last focused
        if self._last_focused_widget == "#bucket-list":
            self.query_one("#bucket-list", BucketList).apply_filter(query)
        else:
            self.query_one("#file-list", FileList).apply_filter(query)

    def on_search_input_search_submitted(
        self, event: SearchInput.SearchSubmitted
    ) -> None:
        """Handle search submission."""
        # Hide search input but keep filter active
        self._search_active = False
        search_container = self.query_one("#search-container")
        search_container.remove_class("visible")

        # Restore focus to the previously focused widget
        self.query_one(self._last_focused_widget).focus()

    def on_search_input_search_cancelled(
        self, event: SearchInput.SearchCancelled
    ) -> None:
        """Handle search cancellation."""
        self.action_cancel_search()

    def on_file_list_preview_requested(
        self, event: FileList.PreviewRequested
    ) -> None:
        """Handle file preview request."""
        obj = event.obj

        if not self._current_bucket:
            return

        try:
            # Check file size
            is_truncated = obj.size > MAX_PREVIEW_SIZE

            # Get file content (limited to MAX_PREVIEW_SIZE)
            content = self.provider.get_object(self._current_bucket, obj.key)

            # Truncate if needed
            if is_truncated:
                content = content[:MAX_PREVIEW_SIZE]

            # Show preview modal
            self.push_screen(PreviewModal(obj, content, is_truncated))
        except Exception as e:
            self.notify(f"Error loading preview: {e}", severity="error")

    def action_switch_account(self) -> None:
        """Switch to the next available account."""
        accounts = get_account_names(self._config)

        if len(accounts) <= 1:
            self.notify("No other accounts configured", severity="warning")
            return

        # Find current account index and get next one
        try:
            current_idx = accounts.index(self._account_name)
            next_idx = (current_idx + 1) % len(accounts)
        except ValueError:
            next_idx = 0

        next_account = accounts[next_idx]
        _, account_config = get_account_config(self._config, next_account)

        try:
            # Create new provider
            self.provider = create_provider(account_config)
            self._account_name = next_account

            # Clear current state
            self._current_bucket = None
            self._current_path = ""

            # Clear file list
            file_list = self.query_one("#file-list", FileList)
            file_list.clear_all()

            # Update path bar
            path_bar = self.query_one("#path-bar", Static)
            path_bar.update("")

            # Reload buckets
            self._load_buckets()

            # Focus bucket list
            self.query_one("#bucket-list", BucketList).focus()

            self.notify(
                f"Switched to account: {next_account} ({account_config.provider})",
                severity="information",
            )
        except Exception as e:
            self.notify(f"Error switching account: {e}", severity="error")

    def on_file_list_download_requested(
        self, event: FileList.DownloadRequested
    ) -> None:
        """Handle file download request."""
        obj = event.obj

        if not self._current_bucket:
            return

        # Determine default download path
        download_dir = DEFAULT_DOWNLOAD_DIR
        if not download_dir.exists():
            download_dir = Path.home()

        default_path = str(download_dir / obj.name)

        # Show input modal for download path
        def handle_download_path(path: str | None) -> None:
            if path is None:
                return  # User cancelled

            self._do_download(obj.key, path)

        self.push_screen(
            InputModal(
                prompt=f"Download '{obj.name}' to:",
                default=default_path,
                placeholder="Enter local file path",
            ),
            handle_download_path,
        )

    def _do_download(self, key: str, local_path: str) -> None:
        """Perform the actual download.

        Args:
            key: The object key to download.
            local_path: The local file path to save to.
        """
        if not self._current_bucket:
            return

        try:
            # Get object content
            self.notify("Downloading...", severity="information")
            content = self.provider.get_object(self._current_bucket, key)

            # Write to local file
            path = Path(local_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

            self.notify(
                f"Downloaded to: {path}",
                severity="information",
            )
        except Exception as e:
            self.notify(f"Download failed: {e}", severity="error")

    def on_file_list_upload_requested(
        self, event: FileList.UploadRequested
    ) -> None:
        """Handle file upload request."""
        if not self._current_bucket:
            self.notify("Please select a bucket first", severity="warning")
            return

        # Show input modal for local file path
        def handle_upload_path(path: str | None) -> None:
            if path is None:
                return  # User cancelled

            self._do_upload(path, event.current_path)

        self.push_screen(
            InputModal(
                prompt="Upload file from:",
                default="",
                placeholder="Enter local file path",
            ),
            handle_upload_path,
        )

    def _do_upload(self, local_path: str, remote_prefix: str) -> None:
        """Perform the actual upload.

        Args:
            local_path: The local file path to upload.
            remote_prefix: The remote path prefix in the bucket.
        """
        if not self._current_bucket:
            return

        try:
            # Read local file
            path = Path(local_path).expanduser()
            if not path.exists():
                self.notify(f"File not found: {path}", severity="error")
                return

            if path.is_dir():
                self.notify("Cannot upload directories", severity="error")
                return

            self.notify("Uploading...", severity="information")
            content = path.read_bytes()

            # Determine remote key
            remote_key = remote_prefix + path.name

            # Upload to OSS
            self.provider.put_object(self._current_bucket, remote_key, content)

            self.notify(
                f"Uploaded: {path.name} -> {remote_key}",
                severity="information",
            )

            # Refresh the file list
            self._load_objects(self._current_bucket, remote_prefix)

        except Exception as e:
            self.notify(f"Upload failed: {e}", severity="error")

    def on_file_list_delete_requested(
        self, event: FileList.DeleteRequested
    ) -> None:
        """Handle file/directory deletion request."""
        obj = event.obj

        if not self._current_bucket:
            return

        # Show confirmation modal
        obj_type = "directory" if obj.is_directory else "file"
        message = f"Delete {obj_type} '{obj.name}'?"

        def handle_confirm(confirmed: bool | None) -> None:
            if confirmed:
                self._do_delete(obj.key, obj.is_directory)

        self.push_screen(ConfirmModal(message), handle_confirm)

    def _do_delete(self, key: str, is_directory: bool) -> None:
        """Perform the actual deletion.

        Args:
            key: The object key to delete.
            is_directory: Whether the object is a directory.
        """
        if not self._current_bucket:
            return

        try:
            if is_directory:
                # For directories, we need to delete all objects with this prefix
                # First, list all objects under this prefix
                self.notify("Deleting directory...", severity="information")
                result = self.provider.list_objects(
                    self._current_bucket,
                    prefix=key,
                    delimiter="",  # No delimiter to get all nested objects
                    max_keys=1000,
                )

                # Delete all objects
                deleted_count = 0
                for obj in result.objects:
                    self.provider.delete_object(self._current_bucket, obj.key)
                    deleted_count += 1

                self.notify(
                    f"Deleted directory: {key} ({deleted_count} objects)",
                    severity="information",
                )
            else:
                # Delete single file
                self.notify("Deleting...", severity="information")
                self.provider.delete_object(self._current_bucket, key)
                self.notify(f"Deleted: {key}", severity="information")

            # Refresh the file list
            self._load_objects(self._current_bucket, self._current_path)

        except Exception as e:
            self.notify(f"Delete failed: {e}", severity="error")
