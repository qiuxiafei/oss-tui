# OSS-TUI 文档

## 概述

OSS-TUI 是一个对象存储服务的终端用户界面（TUI）客户端。它提供了类似 LazyGit 风格的界面，支持 Vim 键位操作，让你能够高效地管理云存储。

## 安装

### 前置要求

- Python 3.11 或更高版本
- 支持 UTF-8 的终端

### 从 PyPI 安装

```bash
pip install oss-tui
```

### 从源码安装

```bash
git clone https://github.com/yourusername/oss-tui.git
cd oss-tui
uv venv && uv sync
uv run oss-tui
```

## 配置

OSS-TUI 按以下顺序查找配置文件：

1. `~/.config/oss-tui/config.toml`
2. `~/.oss-tui.toml`

### 配置格式

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

## 键位绑定

OSS-TUI 使用 Vim 风格的键位进行导航和操作。

### 导航

| 按键          | 操作          |
|---------------|---------------|
| `j` / `↓`     | 向下移动      |
| `k` / `↑`     | 向上移动      |
| `l` / `Enter` | 进入目录      |
| `h` / `Bksp`  | 返回上级      |
| `g` `g`       | 跳到顶部      |
| `G`           | 跳到底部      |
| `Ctrl+d`      | 向下翻页      |
| `Ctrl+u`      | 向上翻页      |

### 操作

| 按键    | 操作         |
|---------|--------------|
| `d`     | 删除         |
| `y`     | 复制（yank） |
| `p`     | 粘贴         |
| `u`     | 上传         |
| `D`     | 下载         |
| `r`     | 刷新         |
| `Space` | 切换选择     |

### 其他

| 按键  | 操作         |
|-------|--------------|
| `/`   | 搜索 / 过滤  |
| `Esc` | 取消 / 清除  |
| `a`   | 切换账户     |
| `?`   | 显示帮助     |
| `q`   | 退出         |

## 支持的服务商

### 文件系统 Provider

文件系统 provider 允许你像操作对象存储一样浏览本地文件系统。这对于开发和测试非常有用。

### 阿里云 OSS

使用阿里云 OSS 需要在配置文件中设置访问凭证。

### 未来计划支持

- AWS S3
- MinIO
- 腾讯云 COS
