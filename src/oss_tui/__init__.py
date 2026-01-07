"""OSS-TUI: A terminal user interface for object storage services."""

__version__ = "0.1.0"


def main() -> None:
    """Entry point for the application."""
    import argparse
    from pathlib import Path

    from oss_tui.app import OssTuiApp
    from oss_tui.config.loader import load_config

    parser = argparse.ArgumentParser(
        description="OSS-TUI: A terminal user interface for object storage services"
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to configuration file",
    )
    parser.add_argument(
        "-a", "--account",
        type=str,
        help="Account name to use (overrides default in config)",
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Create and run app
    app = OssTuiApp(config=config, account=args.account)
    app.run()
