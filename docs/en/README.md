# OSS-TUI Documentation

## Overview

OSS-TUI is a terminal user interface (TUI) client for object storage services. It provides a LazyGit-style interface with Vim keybindings for efficient cloud storage management.

## Installation

### Prerequisites

- Python 3.11 or higher
- A terminal with UTF-8 support

### Install from PyPI

```bash
pip install oss-tui
```

### Install from Source

```bash
git clone https://github.com/yourusername/oss-tui.git
cd oss-tui
uv venv && uv sync
uv run oss-tui
```

## Configuration

OSS-TUI looks for configuration files in the following order:

1. `~/.config/oss-tui/config.toml`
2. `~/.oss-tui.toml`

### Configuration Format

```toml
[default]
provider = "aliyun"
account = "personal"

[accounts.personal]
provider = "aliyun"
endpoint = "oss-cn-hangzhou.aliyuncs.com"
access_key_id = "your-access-key"
access_key_secret = "your-secret-key"

[accounts.work]
provider = "aliyun"
endpoint = "oss-cn-shanghai.aliyuncs.com"
access_key_id = "work-access-key"
access_key_secret = "work-secret-key"
```

## Keybindings

OSS-TUI uses Vim-style keybindings for navigation and operations.

### Navigation

| Key           | Action              |
|---------------|---------------------|
| `j` / `↓`     | Move down           |
| `k` / `↑`     | Move up             |
| `l` / `Enter` | Enter directory     |
| `h` / `Bksp`  | Go back             |
| `g` `g`       | Go to top           |
| `G`           | Go to bottom        |
| `Ctrl+d`      | Page down           |
| `Ctrl+u`      | Page up             |

### Operations

| Key     | Action           |
|---------|------------------|
| `d`     | Delete           |
| `y`     | Copy (yank)      |
| `p`     | Paste            |
| `u`     | Upload           |
| `D`     | Download         |
| `r`     | Refresh          |
| `Space` | Toggle selection |

### Other

| Key   | Action          |
|-------|-----------------|
| `/`   | Search / Filter |
| `Esc` | Cancel / Clear  |
| `a`   | Switch account  |
| `?`   | Show help       |
| `q`   | Quit            |

## Supported Providers

### Filesystem Provider

The filesystem provider allows you to browse your local filesystem as if it were an object storage service. This is useful for development and testing.

### Alibaba Cloud OSS

To use Alibaba Cloud OSS, you need to configure your access credentials in the configuration file.

### Future Providers

- AWS S3
- MinIO
- Tencent Cloud COS
