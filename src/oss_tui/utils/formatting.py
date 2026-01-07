"""Formatting utilities for display."""

from datetime import datetime


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Human-readable size string (e.g., "1.5 MB").
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_time(dt: datetime | None) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format, or None.

    Returns:
        Formatted date string (e.g., "Jan 05") or empty string.
    """
    if dt is None:
        return ""
    return dt.strftime("%b %d")
