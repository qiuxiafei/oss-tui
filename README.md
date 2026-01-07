# OSS-TUI

A terminal user interface (TUI) client for object storage services.

Built with Python and [Textual](https://textual.textualize.io/), OSS-TUI provides a LazyGit-style interface with Vim keybindings for managing your cloud storage.

## Features

- Vim-style keyboard navigation (`j/k/g/G/h/l`)
- Browse buckets and objects
- File operations: download (`D`), upload (`u`), delete (`d`)
- Multi-account support with `a` key switching
- Search and filter (`/` key)
- File preview (`Space` key) with syntax highlighting

## Supported Providers

- [x] Local Filesystem (for development/testing)
- [x] Alibaba Cloud OSS
- [ ] AWS S3 (planned)
- [ ] MinIO (planned)
- [ ] Tencent Cloud COS (planned)

## Installation

### From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/qiuxiafei/oss-tui.git
cd oss-tui

# Create virtual environment and install dependencies
uv venv && uv sync

# Run the application
uv run python -m oss_tui
```

### With uv (without cloning)

```bash
uvx pip install --git https://github.com/qiuxiafei/oss-tui.git
oss-tui
```

### From PyPI (Coming Soon)

```bash
# Not yet published - coming soon!
uv tool install oss-tui
# or
pip install oss-tui
```

## Quick Start

1. **Configure your accounts** (see Configuration section below)

2. **Run the application:**

   ```bash
   # From source
   uv run python -m oss-tui

   # Or after installation
   oss-tui
   ```

3. **Keybindings:**

   | Key | Action |
   |-----|--------|
   | `j` / `k` | Navigate up/down |
   | `g` / `G` | Go to top/bottom |
   | `l` / `Enter` | Enter directory / Select |
   | `h` / `Bksp` | Go back |
   | `Tab` | Switch pane (bucket/file list) |
   | `/` | Search/filter |
   | `Space` | Preview file |
   | `D` | Download file |
   | `u` | Upload file |
   | `d` | Delete file/directory |
   | `a` | Switch account |
   | `r` | Refresh |
   | `?` | Show help |
   | `q` | Quit |

## Configuration

Create a configuration file at `~/.config/oss-tui/config.toml` or `~/.oss-tui.toml`:

```toml
[default]
provider = "filesystem"
account = "local"

[accounts.local]
provider = "filesystem"
root = "~"

[accounts.aliyun-personal]
provider = "aliyun"
endpoint = "oss-cn-hangzhou.aliyuncs.com"
access_key_id = "your-access-key-id"
access_key_secret = "your-secret-key"
```

### Provider Configuration

#### Filesystem (for testing)

```toml
[accounts.local]
provider = "filesystem"
root = "/path/to/directory"  # Optional, defaults to home directory
```

#### Alibaba Cloud OSS

```toml
[accounts.aliyun]
provider = "aliyun"
endpoint = "oss-cn-hangzhou.aliyuncs.com"
access_key_id = "your-access-key-id"
access_key_secret = "your-secret-key"
```

See [config.example.toml](config.example.toml) for more examples.

## Command Line Options

```bash
oss-tui --help
```

```
usage: oss-tui [-h] [-c CONFIG] [-a ACCOUNT]

OSS-TUI: A terminal user interface for object storage services

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file
  -a ACCOUNT, --account ACCOUNT
                        Account name to use (overrides default in config)
```

## Development

```bash
# Clone the repository
git clone https://github.com/qiuxiafei/oss-tui.git
cd oss-tui

# Create virtual environment and install dependencies
uv venv && uv sync

# Run in development mode
uv run python -m oss_tui

# Run tests
uv run pytest -v

# Run linter
uv run ruff check .

# Run linter with auto-fix
uv run ruff check --fix .

# Run type checker
uv run pyright
```

## Documentation

- [English Documentation](docs/en/README.md)
- [中文文档](docs/zh/README.md)

## License

MIT
