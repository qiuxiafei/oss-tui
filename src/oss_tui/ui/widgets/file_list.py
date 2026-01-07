"""File list widget."""

from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from oss_tui.models.object import Object
from oss_tui.utils.formatting import format_size, format_time


class FileListItem(ListItem):
    """A list item representing a file or directory."""

    def __init__(self, obj: Object) -> None:
        """Initialize the file list item.

        Args:
            obj: The object to display.
        """
        super().__init__()
        self.obj = obj

    def compose(self):
        """Compose the list item."""
        icon = "/" if self.obj.is_directory else " "
        size = "" if self.obj.is_directory else format_size(self.obj.size)
        date = format_time(self.obj.last_modified)
        # Format: icon name                    size        date
        # Use fixed widths for proper column alignment
        yield Static(f"{icon} {self.obj.name:<30} {size:>10}  {date:>10}")


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
        ("enter", "select_cursor", "Enter"),
        ("h", "go_back", "Back"),
        ("backspace", "go_back", "Back"),
        ("home", "go_top", "Top"),
        ("end", "go_bottom", "Bottom"),
        ("space", "preview", "Preview"),
        ("D", "download", "Download"),
        ("u", "upload", "Upload"),
        ("d", "delete", "Delete"),
    ]

    class DirectoryEntered(Message):
        """Message sent when entering a directory."""

        def __init__(self, path: str) -> None:
            """Initialize the message.

            Args:
                path: The directory path to enter.
            """
            super().__init__()
            self.path = path

    class GoBack(Message):
        """Message sent when going back to parent directory."""

    class PreviewRequested(Message):
        """Message sent when file preview is requested."""

        def __init__(self, obj: Object) -> None:
            """Initialize the message.

            Args:
                obj: The object to preview.
            """
            super().__init__()
            self.obj = obj

    class DownloadRequested(Message):
        """Message sent when file download is requested."""

        def __init__(self, obj: Object) -> None:
            """Initialize the message.

            Args:
                obj: The object to download.
            """
            super().__init__()
            self.obj = obj

    class UploadRequested(Message):
        """Message sent when file upload is requested."""

        def __init__(self, current_path: str) -> None:
            """Initialize the message.

            Args:
                current_path: The current path in the bucket.
            """
            super().__init__()
            self.current_path = current_path

    class DeleteRequested(Message):
        """Message sent when file/directory deletion is requested."""

        def __init__(self, obj: Object) -> None:
            """Initialize the message.

            Args:
                obj: The object to delete.
            """
            super().__init__()
            self.obj = obj

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the file list."""
        super().__init__(*args, **kwargs)
        self._objects: list[Object] = []
        self._filtered_objects: list[Object] = []
        self._current_path: str = ""
        self._filter_query: str = ""

    @property
    def current_path(self) -> str:
        """Get the current path."""
        return self._current_path

    def load_objects(self, objects: list[Object], path: str = "") -> None:
        """Load objects into the list.

        Args:
            objects: List of objects to display.
            path: Current path in the bucket.
        """
        self._objects = objects
        self._current_path = path
        self._filter_query = ""
        self._refresh_display(objects)

    def _refresh_display(self, objects: list[Object]) -> None:
        """Refresh the display with the given objects.

        Args:
            objects: List of objects to display.
        """
        self._filtered_objects = objects
        self.clear()
        for obj in objects:
            self.append(FileListItem(obj))

    def apply_filter(self, query: str) -> None:
        """Apply a filter to the list.

        Args:
            query: The filter query (case-insensitive).
        """
        self._filter_query = query
        if not query:
            self._refresh_display(self._objects)
        else:
            filtered = [
                obj for obj in self._objects
                if query in obj.name.lower()
            ]
            self._refresh_display(filtered)

    def clear_filter(self) -> None:
        """Clear the current filter and show all objects."""
        self._filter_query = ""
        self._refresh_display(self._objects)

    def clear_all(self) -> None:
        """Clear all objects from the list."""
        self._objects = []
        self._filtered_objects = []
        self._current_path = ""
        self._filter_query = ""
        self.clear()

    def action_go_top(self) -> None:
        """Go to the first item."""
        self.index = 0

    def action_go_bottom(self) -> None:
        """Go to the last item."""
        if self._nodes:
            self.index = len(self._nodes) - 1

    def action_go_back(self) -> None:
        """Go back to parent directory."""
        self.post_message(self.GoBack())

    def action_preview(self) -> None:
        """Request preview of the current item."""
        if self.index is not None and self._nodes:
            item = self._nodes[self.index]
            if isinstance(item, FileListItem):
                obj = item.obj
                # Only preview files, not directories
                if not obj.is_directory:
                    self.post_message(self.PreviewRequested(obj))

    def action_download(self) -> None:
        """Request download of the current item."""
        if self.index is not None and self._nodes:
            item = self._nodes[self.index]
            if isinstance(item, FileListItem):
                obj = item.obj
                # Only download files, not directories
                if not obj.is_directory:
                    self.post_message(self.DownloadRequested(obj))

    def action_upload(self) -> None:
        """Request upload to current path."""
        self.post_message(self.UploadRequested(self._current_path))

    def action_delete(self) -> None:
        """Request deletion of the current item."""
        if self.index is not None and self._nodes:
            item = self._nodes[self.index]
            if isinstance(item, FileListItem):
                self.post_message(self.DeleteRequested(item.obj))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle item selection."""
        if isinstance(event.item, FileListItem):
            obj = event.item.obj
            if obj.is_directory:
                self.post_message(self.DirectoryEntered(obj.key))
