# OSS-TUI

This is an trial on Vibe-Coding with OpenCode as the CLI tool, Claude Opus 4.5 as the backend model and Typeless as the input method.
Here is the share link: https://opncd.ai/share/2nmbG0HX.

-- 

A terminal user interface (TUI) client for object storage services.

Built with Python and [Textual](https://textual.textualize.io/), OSS-TUI provides a LazyGit-style interface with Vim keybindings for managing your cloud storage.

## Features

- Vim-style keyboard navigation
- Browse buckets and objects
- Upload, download, delete, copy, and move objects
- Multi-account support
- Search and filter

## Supported Providers

- [x] Local Filesystem (for development/testing)
- [ ] Alibaba Cloud OSS
- [ ] AWS S3
- [ ] MinIO
- [ ] Tencent Cloud COS

## Installation

```bash
# Using uv (recommended)
uv tool install oss-tui

# Using pip
pip install oss-tui
```

## Quick Start

```bash
# Run the application
oss-tui

# Or with uv
uv run oss-tui
```

## Configuration

Create a configuration file at `~/.config/oss-tui/config.toml` or `~/.oss-tui.toml`:

```toml
[default]
provider = "aliyun"
account = "personal"

[accounts.personal]
provider = "aliyun"
endpoint = "oss-cn-hangzhou.aliyuncs.com"
access_key_id = "your-access-key"
access_key_secret = "your-secret-key"
```

See [config.example.toml](config.example.toml) for more options.

## Documentation

- [English Documentation](docs/en/README.md)
- [中文文档](docs/zh/README.md)

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/oss-tui.git
cd oss-tui

# Create virtual environment and install dependencies
uv venv && uv sync

# Run in development mode
uv run python -m oss_tui

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run type checker
uv run pyright
```

## License

MIT
