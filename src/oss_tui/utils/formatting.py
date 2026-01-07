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


def format_time(dt: datetime | None, include_time: bool = False) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format, or None.
        include_time: Whether to include time in the output.

    Returns:
        Formatted date string (e.g., "2024-01-05 14:30") or empty string.
    """
    if dt is None:
        return ""
    if include_time:
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt.strftime("%Y-%m-%d")
