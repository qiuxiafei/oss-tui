# AGENTS.md - AI Coding Agent Guidelines

This document provides guidelines for AI coding agents working on the OSS-TUI project.

## Project Overview

OSS-TUI is a terminal user interface (TUI) client for object storage services.
Built with Python and Textual, it provides a LazyGit-style interface with Vim keybindings.

**Tech Stack**: Python 3.11+, uv, Textual, oss2, pydantic, pytest, pyright, ruff

## Build / Lint / Test Commands

### Environment Setup

```bash
# Create virtual environment and install dependencies
uv venv && uv sync

# Activate virtual environment (for manual use)
source .venv/bin/activate
```

### Running the Application

```bash
uv run python -m oss_tui
# Or: uv run oss-tui
```

### Linting and Formatting

```bash
uv run ruff check .              # Check code style
uv run ruff check --fix .        # Fix auto-fixable issues
uv run ruff format .             # Format code
uv run ruff format --check .     # Check formatting only
```

### Type Checking

```bash
uv run pyright                   # Run type checker
uv run pyright src/oss_tui/path/to/file.py  # Check specific file
```

### Testing

```bash
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest tests/test_providers/test_filesystem.py  # Single file
uv run pytest tests/test_providers/test_filesystem.py::test_list_buckets  # Single test
uv run pytest -k "test_list"     # Pattern matching
uv run pytest --cov=oss_tui      # With coverage
```

## Project Structure

```
oss-tui/
├── src/oss_tui/
│   ├── __init__.py              # Package version
│   ├── __main__.py              # Entry point
│   ├── app.py                   # Textual App main class
│   ├── config/                  # Configuration management
│   │   ├── settings.py          # Pydantic models
│   │   └── loader.py            # Config file loading
│   ├── providers/               # OSS provider abstraction
│   │   ├── base.py              # Abstract base (Protocol)
│   │   ├── filesystem.py        # Local filesystem provider
│   │   └── aliyun.py            # Alibaba Cloud OSS
│   ├── models/                  # Data models
│   ├── ui/                      # TUI components
│   │   ├── screens/             # Full-screen views
│   │   ├── widgets/             # Reusable widgets
│   │   └── modals/              # Dialog boxes
│   └── utils/                   # Utility functions
├── tests/                       # Test files mirror src structure
├── docs/
│   ├── en/                      # English documentation
│   └── zh/                      # Chinese documentation
└── config.example.toml          # Example configuration
```

## Code Style Guidelines

### Imports

Order imports in groups separated by blank lines:
1. Standard library
2. Third-party packages
3. Local application

```python
import os
from pathlib import Path

from pydantic import BaseModel
from textual.app import App

from oss_tui.models.bucket import Bucket
```

Use absolute imports. Avoid relative imports except within the same subpackage.

### Formatting

- Line length: 88 characters (ruff default)
- Use double quotes for strings
- Use trailing commas in multi-line collections
- Use f-strings for string formatting

### Type Hints

- All public functions must have type hints
- Use `X | None` for nullable types (Python 3.10+ style)
- Use `Protocol` for structural subtyping

```python
from typing import Protocol

class OSSProvider(Protocol):
    def list_buckets(self) -> list[Bucket]: ...
    def list_objects(self, bucket: str, prefix: str = "") -> list[Object]: ...
```

### Naming Conventions

| Element      | Convention       | Example              |
|--------------|------------------|----------------------|
| Modules      | snake_case       | `file_list.py`       |
| Classes      | PascalCase       | `BucketList`         |
| Functions    | snake_case       | `list_objects()`     |
| Variables    | snake_case       | `bucket_name`        |
| Constants    | UPPER_SNAKE_CASE | `DEFAULT_ENDPOINT`   |
| Private      | _leading_under   | `_internal_method()` |

### Docstrings

Use Google-style docstrings:

```python
def upload_object(bucket: str, key: str, data: bytes) -> Object:
    """Upload an object to the specified bucket.

    Args:
        bucket: The name of the target bucket.
        key: The object key (path) in the bucket.
        data: The content to upload.

    Returns:
        The uploaded object metadata.

    Raises:
        BucketNotFoundError: If the bucket does not exist.
    """
```

### Error Handling

- Define custom exceptions in `oss_tui/exceptions.py`
- Use specific exception types, not generic `Exception`
- Include helpful error messages

```python
class OSSError(Exception):
    """Base exception for OSS operations."""

class BucketNotFoundError(OSSError):
    """Raised when the specified bucket does not exist."""
```

### Async Patterns

Use `async/await` for I/O operations. Use Textual's `work` decorator for background tasks:

```python
from textual import work

class MyWidget(Widget):
    @work(exclusive=True)
    async def load_data(self) -> None:
        data = await self.provider.list_objects(self.bucket)
        self.data = data
```

## Provider Implementation

Implementation order:
1. `FilesystemProvider` - Local filesystem (for development/testing)
2. `AliyunOSSProvider` - Alibaba Cloud OSS
3. `S3Provider` - AWS S3 (future)
4. `MinIOProvider` - MinIO (future)
5. `COSProvider` - Tencent Cloud COS (future)

When implementing a new provider:
1. Implement the `OSSProvider` protocol from `providers/base.py`
2. Add provider registration in `providers/__init__.py`
3. Add tests in `tests/test_providers/`
4. Update documentation in `docs/en/` and `docs/zh/`

## UI / Keybindings (Vim-style)

| Key           | Action           | Key       | Action          |
|---------------|------------------|-----------|-----------------|
| `j` / `↓`     | Move down        | `d`       | Delete          |
| `k` / `↑`     | Move up          | `y`       | Copy (yank)     |
| `l` / `Enter` | Enter / Select   | `p`       | Paste           |
| `h` / `Bksp`  | Go back          | `u`       | Upload          |
| `g` / `Home`  | Go to top        | `D`       | Download        |
| `G` / `End`   | Go to bottom     | `r`       | Refresh         |
| `Ctrl+d`      | Page down        | `Space`   | Toggle select   |
| `Ctrl+u`      | Page up          | `a`       | Switch account  |
| `/`           | Search / Filter  | `?`       | Show help       |
| `Esc`         | Cancel / Clear   | `q`       | Quit            |
| `Tab`         | Switch pane      |           |                 |

**Note**: Textual does not support Vim-style multi-key sequences (like `g g`).
Use single key `g` or `Home` for go-to-top instead.

## Configuration

Config file search order:
1. `~/.config/oss-tui/config.toml`
2. `~/.oss-tui.toml`

See `config.example.toml` for format details.

## Git Commit Rules

**IMPORTANT**: Before every git commit, you MUST:

1. Update `AGENTS.md` if any conventions, patterns, or technical decisions have changed
2. Update `TODO.md` to reflect completed tasks and any new tasks discovered
3. Run `uv run ruff check .` and `uv run pyright` to ensure code quality
4. Run `uv run pytest` to ensure all tests pass

This ensures project documentation stays in sync with the codebase.

## Communication

- Code comments and documentation: **English**
- Developer conversations: **Chinese (中文)**
