"""Tests for file detection utilities."""

import pytest

from oss_tui.utils.file_detection import (
    detect_file_type,
    get_file_extension,
    get_syntax_lexer,
    is_text_by_content,
    is_text_by_extension,
)


class TestGetFileExtension:
    """Test cases for get_file_extension function."""

    def test_python_file(self):
        """Test getting extension from Python file."""
        assert get_file_extension("test.py") == ".py"
        assert get_file_extension("path/to/test.py") == ".py"
        assert get_file_extension("test.PY") == ".py"

    def test_no_extension(self):
        """Test getting extension from file without extension."""
        assert get_file_extension("Makefile") == ""
        assert get_file_extension("README") == ""

    def test_multiple_dots(self):
        """Test getting extension with multiple dots."""
        assert get_file_extension("test.min.js") == ".js"
        assert get_file_extension("archive.tar.gz") == ".gz"

    def test_special_files(self):
        """Test getting extension from files with path separators."""
        assert get_file_extension("/path/to/file.txt") == ".txt"
        assert get_file_extension("C:\\path\\to\\file.txt") == ".txt"


class TestIsTextByExtension:
    """Test cases for is_text_by_extension function."""

    def test_python_file(self):
        """Test Python file is text."""
        assert is_text_by_extension("test.py") is True
        assert is_text_by_extension("script.js") is True
        assert is_text_by_extension("data.json") is True

    def test_binary_files(self):
        """Test binary files are detected."""
        assert is_text_by_extension("image.png") is False
        assert is_text_by_extension("archive.zip") is False
        assert is_text_by_extension("image.jpg") is False

    def test_special_filenames(self):
        """Test special filenames are detected."""
        assert is_text_by_extension("Dockerfile") is True
        assert is_text_by_extension("Makefile") is True
        assert is_text_by_extension("README.md") is True

    def test_unknown_extension(self):
        """Test unknown extensions return None."""
        assert is_text_by_extension("file.xyz") is None
        assert is_text_by_extension("data.unknown") is None


class TestIsTextByContent:
    """Test cases for is_text_by_content function."""

    def test_text_content(self):
        """Test text content is detected."""
        assert is_text_by_content(b"Hello, World!") is True
        assert is_text_by_content(b'{"key": "value"}') is True
        assert is_text_by_content(b"def hello():\n    pass") is True

    def test_binary_content(self):
        """Test binary content is detected."""
        # Use actual null bytes which indicate binary
        assert is_text_by_content(b"Hello\x00World") is False
        assert is_text_by_content(b"\x00\x00\x00") is False
        # PNG-like header with null bytes
        assert is_text_by_content(b"\x89PNG\x00\x0d\x0a\x1a\x0a") is False

    def test_null_bytes(self):
        """Test null bytes indicate binary."""
        assert is_text_by_content(b"Hello\x00World") is False

    def test_utf8_content(self):
        """Test UTF-8 content with unicode."""
        assert is_text_by_content("你好世界".encode("utf-8")) is True
        assert is_text_by_content("Hello 🌍".encode("utf-8")) is True


class TestDetectFileType:
    """Test cases for detect_file_type function."""

    def test_text_file_by_extension(self):
        """Test text file detection by extension."""
        assert detect_file_type("test.py") is True
        assert detect_file_type("data.json") is True

    def test_binary_file_by_extension(self):
        """Test binary file detection by extension."""
        assert detect_file_type("image.png") is False
        assert detect_file_type("archive.zip") is False

    def test_unknown_file_with_content(self):
        """Test unknown file with text content."""
        content = b"This is a text file"
        assert detect_file_type("data.xyz", content) is True

    def test_unknown_file_with_binary_content(self):
        """Test unknown file with binary content."""
        content = b"\x89PNG\x00\x0d\x0a\x1a\x0a"
        assert detect_file_type("data.xyz", content) is False

    def test_no_content_defaults_to_binary(self):
        """Test file with no content defaults to binary."""
        assert detect_file_type("unknown.xyz") is False


class TestGetSyntaxLexer:
    """Test cases for get_syntax_lexer function."""

    def test_python_lexer(self):
        """Test Python file gets python lexer."""
        assert get_syntax_lexer("test.py") == "python"
        assert get_syntax_lexer("script.py") == "python"

    def test_javascript_lexer(self):
        """Test JavaScript file gets javascript lexer."""
        assert get_syntax_lexer("test.js") == "javascript"
        assert get_syntax_lexer("test.ts") == "typescript"
        assert get_syntax_lexer("test.jsx") == "jsx"

    def test_markup_lexer(self):
        """Test markup files get correct lexers."""
        assert get_syntax_lexer("page.html") == "html"
        assert get_syntax_lexer("style.css") == "css"
        assert get_syntax_lexer("doc.md") == "markdown"

    def test_config_lexer(self):
        """Test config files get correct lexers."""
        assert get_syntax_lexer("config.json") == "json"
        assert get_syntax_lexer("config.yaml") == "yaml"
        assert get_syntax_lexer("config.toml") == "toml"

    def test_shell_lexer(self):
        """Test shell scripts get bash lexer."""
        assert get_syntax_lexer("script.sh") == "bash"
        assert get_syntax_lexer("script.zsh") == "zsh"

    def test_special_files(self):
        """Test special filenames get correct lexers."""
        assert get_syntax_lexer("Dockerfile") == "dockerfile"
        assert get_syntax_lexer("Makefile") == "makefile"
        assert get_syntax_lexer("docker-compose.yml") == "yaml"

    def test_unknown_lexer(self):
        """Test unknown file returns None."""
        assert get_syntax_lexer("data.xyz") is None
        assert get_syntax_lexer("README") is None
