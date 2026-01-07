"""File type detection utilities."""

# Common text file extensions
TEXT_EXTENSIONS: set[str] = {
    # Programming languages
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".pl",
    ".pm",
    ".lua",
    ".r",
    ".R",
    ".m",
    ".mm",
    # Web
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".vue",
    ".svelte",
    # Data formats
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".properties",
    ".csv",
    ".tsv",
    # Documentation
    ".md",
    ".markdown",
    ".rst",
    ".txt",
    ".text",
    ".rtf",
    # Shell scripts
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".ps1",
    ".bat",
    ".cmd",
    # Config files
    ".env",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".dockerignore",
    ".eslintrc",
    ".prettierrc",
    # Other
    ".log",
    ".sql",
    ".graphql",
    ".gql",
    ".proto",
    ".tf",
    ".hcl",
    ".makefile",
    ".dockerfile",
    ".cmake",
}

# Files without extension that are typically text
TEXT_FILENAMES: set[str] = {
    "Makefile",
    "Dockerfile",
    "Jenkinsfile",
    "Vagrantfile",
    "Gemfile",
    "Rakefile",
    "Procfile",
    "README",
    "LICENSE",
    "CHANGELOG",
    "AUTHORS",
    "CONTRIBUTORS",
    "COPYING",
    "INSTALL",
    "TODO",
    "NOTICE",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".dockerignore",
}

# Maximum bytes to check for binary detection
BINARY_CHECK_SIZE = 8192


def get_file_extension(filename: str) -> str:
    """Get the file extension (lowercase).

    Args:
        filename: The filename to check.

    Returns:
        The file extension including the dot, or empty string.
    """
    if "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    return ""


def is_text_by_extension(filename: str) -> bool | None:
    """Check if a file is text based on its extension.

    Args:
        filename: The filename to check.

    Returns:
        True if definitely text, False if definitely binary, None if unknown.
    """
    # Check known text filenames
    basename = filename.rstrip("/").split("/")[-1]
    if basename in TEXT_FILENAMES:
        return True

    ext = get_file_extension(filename)
    if ext in TEXT_EXTENSIONS:
        return True

    # Known binary extensions
    binary_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".webp",
        ".svg",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".dat",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wav",
        ".flac",
        ".ogg",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".eot",
        ".pyc",
        ".pyo",
        ".class",
        ".o",
        ".obj",
        ".a",
        ".lib",
    }
    if ext in binary_extensions:
        return False

    return None  # Unknown, need to check content


def is_text_by_content(data: bytes) -> bool:
    """Check if content is text by looking for null bytes.

    Args:
        data: The content bytes to check (first 8KB recommended).

    Returns:
        True if content appears to be text, False otherwise.
    """
    # Check for null bytes (common in binary files)
    if b"\x00" in data:
        return False

    # Try to decode as UTF-8
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        pass

    # Try common encodings
    for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
        try:
            data.decode(encoding)
            return True
        except UnicodeDecodeError:
            continue

    return False


def detect_file_type(filename: str, content: bytes | None = None) -> bool:
    """Detect if a file is text or binary.

    Args:
        filename: The filename to check.
        content: Optional content bytes for content-based detection.

    Returns:
        True if the file is text, False if binary.
    """
    # First try extension-based detection
    result = is_text_by_extension(filename)
    if result is not None:
        return result

    # If we have content, check it
    if content is not None:
        check_bytes = content[:BINARY_CHECK_SIZE]
        return is_text_by_content(check_bytes)

    # Default to binary if we can't determine
    return False


def get_syntax_lexer(filename: str) -> str | None:
    """Get the syntax lexer name for a file based on its extension.

    Args:
        filename: The filename to check.

    Returns:
        The Pygments lexer name, or None if unknown.
    """
    ext = get_file_extension(filename)
    basename = filename.rstrip("/").split("/")[-1].lower()

    # Extension to lexer mapping
    lexer_map: dict[str, str] = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".lua": "lua",
        ".r": "r",
        ".R": "r",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        ".vue": "vue",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xml": "xml",
        ".toml": "toml",
        ".ini": "ini",
        ".md": "markdown",
        ".markdown": "markdown",
        ".rst": "rst",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".ps1": "powershell",
        ".bat": "batch",
        ".sql": "sql",
        ".graphql": "graphql",
        ".proto": "protobuf",
        ".tf": "terraform",
        ".dockerfile": "dockerfile",
        ".makefile": "makefile",
    }

    # Check basename for special files
    if basename == "dockerfile":
        return "dockerfile"
    if basename == "makefile":
        return "makefile"

    return lexer_map.get(ext)
