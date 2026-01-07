"""Help modal dialog."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static

HELP_TEXT = """\
OSS-TUI Keybindings

Navigation:
  j / ↓       Move down
  k / ↑       Move up
  l / Enter   Enter directory
  h / Bksp    Go back
  g g         Go to top
  G           Go to bottom
  Ctrl+d      Page down
  Ctrl+u      Page up

Operations:
  d           Delete
  y           Copy (yank)
  p           Paste
  u           Upload
  D           Download
  r           Refresh
  Space       Toggle selection

Other:
  /           Search / Filter
  Esc         Cancel / Clear
  a           Switch account
  ?           Show this help
  q           Quit

Press any key to close...
"""


class HelpModal(ModalScreen):
    """A modal dialog showing help information."""

    BINDINGS = [("escape", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        """Compose the help modal."""
        yield Static(HELP_TEXT)

    def on_key(self, event) -> None:
        """Close on any key press."""
        self.dismiss()
