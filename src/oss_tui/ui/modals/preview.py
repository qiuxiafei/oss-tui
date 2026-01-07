"""Preview modal for file content display."""

from rich.syntax import Syntax
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from oss_tui.models.object import Object
from oss_tui.utils.file_detection import detect_file_type, get_syntax_lexer
from oss_tui.utils.formatting import format_size

# Maximum file size to load for preview (100KB)
MAX_PREVIEW_SIZE = 100 * 1024


class PreviewModal(ModalScreen[None]):
    """A modal screen for previewing file contents.

    Displays text files with syntax highlighting and metadata for binary files.
    Supports Vim-style scrolling with j/k keys.
    """

    BINDINGS = [
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("ctrl+d", "page_down", "Page Down", show=False),
        Binding("ctrl+u", "page_up", "Page Up", show=False),
        Binding("g", "scroll_home", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    CSS = """
    PreviewModal {
        align: center middle;
    }

    PreviewModal > Vertical {
        width: 90%;
        height: 80%;
        border: thick $primary;
        background: $surface;
    }

    PreviewModal #preview-header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
        text-style: bold;
    }

    PreviewModal #preview-scroll {
        height: 1fr;
        padding: 1;
    }

    PreviewModal #preview-content {
        width: 100%;
    }

    PreviewModal #preview-footer {
        height: 1;
        background: $surface-darken-1;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        obj: Object,
        content: bytes | None = None,
        is_truncated: bool = False,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the preview modal.

        Args:
            obj: The object metadata.
            content: The file content (None for binary files).
            is_truncated: Whether the content was truncated.
        """
        super().__init__(*args, **kwargs)
        self.obj = obj
        self.content = content
        self.is_truncated = is_truncated

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical():
            yield Static(f"Preview: {self.obj.name}", id="preview-header")
            with VerticalScroll(id="preview-scroll"):
                yield Static("", id="preview-content")
            footer_text = "[j/k] Scroll  [g/G] Top/Bottom  [ESC/q] Close"
            if self.is_truncated:
                footer_text = f"[Truncated to {format_size(MAX_PREVIEW_SIZE)}]  " + footer_text
            yield Static(footer_text, id="preview-footer")

    def on_mount(self) -> None:
        """Handle mount event."""
        self._render_content()

    def _render_content(self) -> None:
        """Render the file content."""
        content_widget = self.query_one("#preview-content", Static)

        # Check if this is a text file
        is_text = detect_file_type(self.obj.key, self.content)

        if not is_text or self.content is None:
            # Show metadata only for binary files
            self._show_metadata(content_widget)
        else:
            # Show text content with syntax highlighting
            self._show_text_content(content_widget)

    def _show_metadata(self, content_widget: Static) -> None:
        """Display file metadata only.

        Args:
            content_widget: The widget to update.
        """
        lines = [
            f"File: {self.obj.name}",
            f"Path: {self.obj.key}",
            f"Size: {format_size(self.obj.size)}",
        ]

        if self.obj.last_modified:
            lines.append(f"Modified: {self.obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.obj.content_type:
            lines.append(f"Type: {self.obj.content_type}")

        if self.obj.etag:
            lines.append(f"ETag: {self.obj.etag}")

        lines.append("")
        lines.append("[Binary file - preview not available]")

        content_widget.update(Text("\n".join(lines)))

    def _show_text_content(self, content_widget: Static) -> None:
        """Display text content with syntax highlighting.

        Args:
            content_widget: The widget to update.
        """
        if self.content is None:
            return

        # Decode content
        try:
            text = self.content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = self.content.decode("latin-1")
            except UnicodeDecodeError:
                self._show_metadata(content_widget)
                return

        # Get syntax lexer
        lexer = get_syntax_lexer(self.obj.key)

        if lexer:
            # Use syntax highlighting
            syntax = Syntax(
                text,
                lexer,
                theme="monokai",
                line_numbers=True,
                word_wrap=False,
            )
            content_widget.update(syntax)
        else:
            # Plain text
            content_widget.update(Text(text))

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss(None)

    def action_scroll_down(self) -> None:
        """Scroll down one line."""
        scroll = self.query_one("#preview-scroll", VerticalScroll)
        scroll.scroll_relative(y=1)

    def action_scroll_up(self) -> None:
        """Scroll up one line."""
        scroll = self.query_one("#preview-scroll", VerticalScroll)
        scroll.scroll_relative(y=-1)

    def action_page_down(self) -> None:
        """Scroll down one page."""
        scroll = self.query_one("#preview-scroll", VerticalScroll)
        scroll.scroll_relative(y=scroll.size.height)

    def action_page_up(self) -> None:
        """Scroll up one page."""
        scroll = self.query_one("#preview-scroll", VerticalScroll)
        scroll.scroll_relative(y=-scroll.size.height)

    def action_scroll_home(self) -> None:
        """Scroll to the top."""
        scroll = self.query_one("#preview-scroll", VerticalScroll)
        scroll.scroll_home()

    def action_scroll_end(self) -> None:
        """Scroll to the bottom."""
        scroll = self.query_one("#preview-scroll", VerticalScroll)
        scroll.scroll_end()
