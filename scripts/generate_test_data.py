#!/usr/bin/env python3
"""Generate a test directory structure with various file types for OSS testing.

This script creates a local directory with 4-5 levels of subdirectories
containing text files, code files, and binary files.
"""

import argparse
import random
import struct
from pathlib import Path

# Text content samples
TEXT_CONTENTS = [
    "Hello, World! This is a simple text file for testing.",
    """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
""",
    """# Meeting Notes

## Date: 2024-01-15

### Attendees
- Alice
- Bob
- Charlie

### Discussion Points
1. Project timeline review
2. Resource allocation
3. Next sprint planning

### Action Items
- [ ] Update documentation
- [ ] Review pull requests
- [ ] Schedule follow-up meeting
""",
    """Configuration Notes
==================

Server: production-01
Region: us-east-1
Status: Active

Last updated: 2024-01-15
""",
]

# Python code samples
PYTHON_CODE_SAMPLES = [
    '''"""A simple utility module."""


def hello(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    print(hello("World"))
    print(f"5! = {factorial(5)}")
''',
    '''"""Data processing utilities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Record:
    """A simple data record."""

    id: int
    name: str
    value: float


def process_records(records: list[Record]) -> dict[str, Any]:
    """Process a list of records and return statistics."""
    if not records:
        return {"count": 0, "total": 0.0, "average": 0.0}

    total = sum(r.value for r in records)
    return {
        "count": len(records),
        "total": total,
        "average": total / len(records),
    }
''',
]

# JavaScript code samples
JS_CODE_SAMPLES = [
    '''// Simple utility functions

function greet(name) {
    return `Hello, ${name}!`;
}

function sum(numbers) {
    return numbers.reduce((acc, n) => acc + n, 0);
}

function filterPositive(numbers) {
    return numbers.filter(n => n > 0);
}

export { greet, sum, filterPositive };
''',
    '''// API client module

class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async get(endpoint) {
        const response = await fetch(`${this.baseUrl}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
    }

    async post(endpoint, data) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.json();
    }
}

export default ApiClient;
''',
]

# JSON samples
JSON_SAMPLES = [
    """{
    "name": "test-project",
    "version": "1.0.0",
    "description": "A test project",
    "dependencies": {
        "lodash": "^4.17.21",
        "axios": "^1.6.0"
    }
}
""",
    """{
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ],
    "metadata": {
        "total": 3,
        "page": 1
    }
}
""",
]

# YAML samples
YAML_SAMPLES = [
    """# Application configuration
app:
  name: my-service
  version: 1.0.0
  port: 8080

database:
  host: localhost
  port: 5432
  name: mydb

logging:
  level: INFO
  format: json
""",
    """# Docker compose configuration
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
""",
]

# Markdown samples
MARKDOWN_SAMPLES = [
    """# Project README

## Overview

This is a sample project for testing purposes.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from mymodule import hello
print(hello("World"))
```

## License

MIT License
""",
    """# API Documentation

## Endpoints

### GET /api/users

Returns a list of all users.

**Response:**
```json
{
    "users": [...],
    "total": 100
}
```

### POST /api/users

Create a new user.

**Request Body:**
```json
{
    "name": "string",
    "email": "string"
}
```
""",
]

# Directory structure template
DIRECTORY_STRUCTURE = {
    "documents": {
        "reports": {
            "2024": {
                "q1": {},
                "q2": {},
            },
            "archive": {},
        },
        "notes": {},
    },
    "src": {
        "lib": {
            "utils": {},
            "helpers": {},
        },
        "components": {
            "common": {},
        },
        "tests": {},
    },
    "data": {
        "raw": {
            "images": {},
            "datasets": {},
        },
        "processed": {},
        "cache": {},
    },
    "config": {
        "environments": {
            "dev": {},
            "prod": {},
        },
    },
}


def generate_binary_content(size: int) -> bytes:
    """Generate random binary content of specified size."""
    # Mix of random bytes and some structured data
    content = bytearray()

    # Add a simple header
    content.extend(b"\x89PNG\r\n\x1a\n")  # PNG-like header

    # Add random data
    while len(content) < size:
        # Mix of random bytes and some patterns
        if random.random() < 0.3:
            # Add some structured data
            content.extend(struct.pack("<I", random.randint(0, 2**32 - 1)))
        else:
            # Add random bytes
            content.extend(bytes([random.randint(0, 255) for _ in range(min(64, size - len(content)))]))

    return bytes(content[:size])


def create_text_file(path: Path) -> None:
    """Create a text file with sample content."""
    content = random.choice(TEXT_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_python_file(path: Path) -> None:
    """Create a Python file with sample code."""
    content = random.choice(PYTHON_CODE_SAMPLES)
    path.write_text(content, encoding="utf-8")


def create_js_file(path: Path) -> None:
    """Create a JavaScript file with sample code."""
    content = random.choice(JS_CODE_SAMPLES)
    path.write_text(content, encoding="utf-8")


def create_json_file(path: Path) -> None:
    """Create a JSON file with sample data."""
    content = random.choice(JSON_SAMPLES)
    path.write_text(content, encoding="utf-8")


def create_yaml_file(path: Path) -> None:
    """Create a YAML file with sample config."""
    content = random.choice(YAML_SAMPLES)
    path.write_text(content, encoding="utf-8")


def create_markdown_file(path: Path) -> None:
    """Create a Markdown file with sample content."""
    content = random.choice(MARKDOWN_SAMPLES)
    path.write_text(content, encoding="utf-8")


def create_binary_file(path: Path, size: int | None = None) -> None:
    """Create a binary file with random content."""
    if size is None:
        size = random.randint(1024, 10240)  # 1KB to 10KB
    content = generate_binary_content(size)
    path.write_bytes(content)


def create_image_placeholder(path: Path) -> None:
    """Create a simple binary file as image placeholder."""
    # Create a minimal valid-ish binary that looks like an image header
    size = random.randint(2048, 8192)
    create_binary_file(path, size)


# File type generators
FILE_GENERATORS = {
    ".txt": create_text_file,
    ".py": create_python_file,
    ".js": create_js_file,
    ".json": create_json_file,
    ".yaml": create_yaml_file,
    ".yml": create_yaml_file,
    ".md": create_markdown_file,
    ".bin": create_binary_file,
    ".dat": create_binary_file,
    ".png": create_image_placeholder,
    ".jpg": create_image_placeholder,
}

# Files to create in specific directories
DIRECTORY_FILES = {
    "documents/reports/2024/q1": [
        "report_january.txt",
        "report_february.md",
        "summary.json",
    ],
    "documents/reports/2024/q2": [
        "report_april.txt",
        "metrics.json",
    ],
    "documents/reports/archive": [
        "old_report_2023.txt",
        "archive_data.bin",
    ],
    "documents/notes": [
        "meeting_notes.md",
        "todo.txt",
        "ideas.md",
    ],
    "src/lib/utils": [
        "helpers.py",
        "formatters.py",
        "validators.js",
    ],
    "src/lib/helpers": [
        "string_utils.py",
        "date_utils.js",
    ],
    "src/components/common": [
        "button.js",
        "modal.js",
        "styles.json",
    ],
    "src/tests": [
        "test_utils.py",
        "test_helpers.py",
        "fixtures.json",
    ],
    "data/raw/images": [
        "sample_001.png",
        "sample_002.jpg",
        "sample_003.png",
    ],
    "data/raw/datasets": [
        "training_data.bin",
        "validation_data.bin",
        "metadata.json",
    ],
    "data/processed": [
        "output.dat",
        "results.json",
        "summary.txt",
    ],
    "data/cache": [
        "cache_001.bin",
        "cache_002.bin",
    ],
    "config/environments/dev": [
        "config.yaml",
        "secrets.json",
    ],
    "config/environments/prod": [
        "config.yaml",
        "deployment.yml",
    ],
}


def create_directory_structure(base_path: Path, structure: dict) -> None:
    """Recursively create directory structure."""
    for name, substructure in structure.items():
        dir_path = base_path / name
        dir_path.mkdir(parents=True, exist_ok=True)
        if substructure:
            create_directory_structure(dir_path, substructure)


def create_files(base_path: Path) -> int:
    """Create files in the directory structure."""
    file_count = 0

    for rel_dir, files in DIRECTORY_FILES.items():
        dir_path = base_path / rel_dir
        dir_path.mkdir(parents=True, exist_ok=True)

        for filename in files:
            file_path = dir_path / filename
            ext = file_path.suffix.lower()

            generator = FILE_GENERATORS.get(ext, create_text_file)
            generator(file_path)
            file_count += 1
            print(f"  Created: {file_path.relative_to(base_path)}")

    return file_count


def create_root_files(base_path: Path) -> int:
    """Create some files in the root directory."""
    root_files = [
        "README.md",
        "config.json",
        ".gitignore",
    ]

    file_count = 0
    for filename in root_files:
        file_path = base_path / filename
        ext = file_path.suffix.lower() if file_path.suffix else ".txt"

        if filename == ".gitignore":
            file_path.write_text(
                """# Generated gitignore
*.pyc
__pycache__/
.env
.venv/
node_modules/
*.log
""",
                encoding="utf-8",
            )
        else:
            generator = FILE_GENERATORS.get(ext, create_text_file)
            generator(file_path)

        file_count += 1
        print(f"  Created: {filename}")

    return file_count


def generate_test_directory(output_path: str | Path, seed: int | None = None) -> None:
    """Generate a complete test directory structure.

    Args:
        output_path: Path where the test directory will be created.
        seed: Random seed for reproducible generation.
    """
    if seed is not None:
        random.seed(seed)

    base_path = Path(output_path)

    if base_path.exists():
        print(f"Warning: Directory '{base_path}' already exists.")
        response = input("Do you want to continue and add files? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return

    print(f"\nGenerating test directory at: {base_path.absolute()}\n")

    # Create directory structure
    print("Creating directory structure...")
    base_path.mkdir(parents=True, exist_ok=True)
    create_directory_structure(base_path, DIRECTORY_STRUCTURE)

    # Create files
    print("\nCreating files...")
    file_count = create_root_files(base_path)
    file_count += create_files(base_path)

    # Summary
    print(f"\n{'=' * 50}")
    print("Test directory generated successfully!")
    print(f"  Location: {base_path.absolute()}")
    print(f"  Total files created: {file_count}")

    # Count directories
    dir_count = sum(1 for _ in base_path.rglob("*") if _.is_dir())
    print(f"  Total directories: {dir_count}")
    print(f"{'=' * 50}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a test directory structure for OSS testing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Create in ./test_data
  %(prog)s -o /tmp/oss_test         # Create in /tmp/oss_test
  %(prog)s --seed 42                # Use fixed seed for reproducibility
""",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="test_data",
        help="Output directory path (default: ./test_data)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible generation",
    )

    args = parser.parse_args()
    generate_test_directory(args.output, args.seed)


if __name__ == "__main__":
    main()
