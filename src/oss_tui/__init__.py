"""OSS-TUI: A terminal user interface for object storage services."""

__version__ = "0.1.0"


def main() -> None:
    """Entry point for the application."""
    from oss_tui.app import OssTuiApp

    app = OssTuiApp()
    app.run()
