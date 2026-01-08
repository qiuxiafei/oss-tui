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

# Log file samples
LOG_CONTENTS = [
    """[2024-01-15T10:00:00] INFO: Application started successfully
[2024-01-15T10:00:01] DEBUG: Loading configuration
[2024-01-15T10:00:02] INFO: Connected to database
[2024-01-15T10:00:03] DEBUG: Initializing services
[2024-01-15T10:00:04] INFO: Server listening on port 8080
[2024-01-15T10:01:15] INFO: Processing request from 192.168.1.100
[2024-01-15T10:01:20] DEBUG: Request completed in 5.2s
[2024-01-15T10:02:10] WARN: High memory usage detected
[2024-01-15T10:03:45] INFO: Scheduled task executed
""",
    """2024-01-15 09:30:15,320 - app - ERROR - Database connection failed
2024-01-15 09:30:16,100 - app - ERROR - Retrying in 5 seconds
2024-01-15 09:30:22,200 - app - ERROR - Max retries exceeded
2024-01-15 09:30:22,250 - app - CRITICAL - Service unavailable
2024-01-15 09:30:30,000 - app - ERROR - No such file: 'data/queue/1e2a3b4c.log'
""",
]

# CSV data samples
CSV_CONTENTS = [
    """id,name,email,created_at
1,Alice Smith,alice@example.com,2024-01-10T10:00:00Z
2,Bob Johnson,bob@example.com,2024-01-11T11:00:00Z
3,Charlie Brown,charlie@example.com,2024-01-12T12:00:00Z
""",
    """timestamp,value,sensor_id
1705315200,23.5,TEMP_001
1705315260,24.1,TEMP_001
1705315320,23.8,TEMP_001
1705315380,25.2,TEMP_001
""",
]

# SQL sample
SQL_CONTENTS = [
    """-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (name, email) VALUES 
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');

-- Create index
CREATE INDEX idx_users_email ON users(email);
""",
    """-- Query example
SELECT 
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.amount) as total_amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.created_at >= '2024-01-01'
GROUP BY u.id
ORDER BY total_amount DESC
LIMIT 10;
""",
]

# HTML sample
HTML_CONTENTS = [
    """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a test HTML page.</p>
</body>
</html>
""",
    """<!DOCTYPE html>
<html>
<head>
    <title>Table Example</title>
</head>
<body>
    <table>
        <tr><th>ID</th><th>Name</th><th>Value</th></tr>
        <tr><td>1</td><td>Item A</td><td>100</td></tr>
        <tr><td>2</td><td>Item B</td><td>200</td></tr>
    </table>
</body>
</html>
""",
]

# Java code sample
JAVA_CONTENTS = [
    '''// User class
public class User {
    private int id;
    private String name;
    
    public User(int id, String name) {
        this.id = id;
        this.name = name;
    }
    
    public int getId() { return id; }
    public String getName() { return name; }
}
''',
    '''// Main class
import java.util.*;
import java.util.stream.*;

public class App {
    public static void main(String[] args) {
        List<User> users = Arrays.asList(
            new User(1, "Alice"),
            new User(2, "Bob"),
            new User(3, "Charlie")
        );
        
        users.stream()
            .filter(u -> u.getId() > 1)
            .forEach(u -> System.out.println(u.getName()));
    }
}
''',
]

# C++ code sample
CPP_CONTENTS = [
    '''// Sample class
#include <iostream>
#include <vector>

class Calculator {
public:
    int add(int a, int b) { return a + b; }
    int multiply(int a, int b) { return a * b; }
};

int main() {
    Calculator calc;
    std::cout << "5 + 3 = " << calc.add(5, 3) << std::endl;
    return 0;
}
''',
    '''// Template example
#include <iostream>
#include <vector>
#include <algorithm>

template<typename T>
T findMax(const std::vector<T>& vec) {
    if (vec.empty()) return T{};
    return *std::max_element(vec.begin(), vec.end());
}
''',
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


def create_log_file(path: Path) -> None:
    """Create a log file with sample content."""
    content = random.choice(LOG_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_csv_file(path: Path) -> None:
    """Create a CSV file with sample data."""
    content = random.choice(CSV_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_sql_file(path: Path) -> None:
    """Create a SQL file with sample queries."""
    content = random.choice(SQL_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_html_file(path: Path) -> None:
    """Create a HTML file with sample content."""
    content = random.choice(HTML_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_java_file(path: Path) -> None:
    """Create a Java file with sample code."""
    content = random.choice(JAVA_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_cpp_file(path: Path) -> None:
    """Create a C++ file with sample code."""
    content = random.choice(CPP_CONTENTS)
    path.write_text(content, encoding="utf-8")


def create_tiny_file(path: Path) -> None:
    """Create a very small file."""
    if path.suffix in [".txt", ".md"]:
        content = f"# {path.stem}\n\nA very small {path.suffix[1:].upper()} file."
        path.write_text(content, encoding="utf-8")
    else:
        # 1-5 个字符/字节的极小文件
        if path.suffix in [".json", ".log", ".js", ".py"]:
            path.write_text("void", encoding="utf-8")
        else:
            path.write_bytes(b"\x00" * random.randint(1, 5))


def create_huge_binary(path: Path) -> None:
    """Create a relatively large binary file for testing larger uploads."""
    # 1MB - 10MB
    size = random.randint(1024 * 1024, 10 * 1024 * 1024)
    content = generate_binary_content(size)
    path.write_bytes(content)


# Extended file type generators
FILE_GENERATORS = {
    ".txt": create_text_file,
    ".py": create_python_file,
    ".js": create_js_file,
    ".json": create_json_file,
    ".yaml": create_yaml_file,
    ".yml": create_yaml_file,
    ".md": create_markdown_file,
    ".log": create_log_file,
    ".csv": create_csv_file,
    ".sql": create_sql_file,
    ".html": create_html_file,
    ".htm": create_html_file,
    ".java": create_java_file,
    ".cpp": create_cpp_file,
    ".cc": create_cpp_file,
    ".h": create_cpp_file,
    ".hpp": create_cpp_file,
    ".bin": create_binary_file,
    ".dat": create_binary_file,
    ".tmp": create_binary_file,
    ".cache": create_binary_file,
    ".png": create_image_placeholder,
    ".jpg": create_image_placeholder,
    ".jpeg": create_image_placeholder,
    ".gif": create_image_placeholder,
    ".ico": create_image_placeholder,
    ".tiff": create_image_placeholder,
    ".mp3": create_huge_binary,  # 大文件
    ".mp4": create_huge_binary,  # 大文件
    ".avi": create_huge_binary,  # 大文件
}

# Random file name components for different directories
FILE_NAME_TEMPLATES = {
    "documents": [
        "report_{year}_{month}",
        "summary_{date}",
        "notes_{date}",
        "meeting_{date}",
        "agenda_{date}",
        "briefing_{date}",
        "review_{date}",
        "analysis_{date}",
        "feedback_{date}",
        "approval_{date}",
    ],
    "src": [
        "module_{num}",
        "helper_{num}",
        "util_{num}",
        "service_{num}",
        "manager_{num}",
        "controller_{num}",
        "model_{num}",
        "repository_{num}",
        "factory_{num}",
        "processor_{num}",
    ],
    "data": [
        "data_{num}",
        "dataset_{num}",
        "cache_{num}",
        "temp_{num}",
        "batch_{num}",
        "chunk_{num}",
        "segment_{num}",
        "block_{num}",
        "record_{num}",
        "entry_{num}",
    ],
    "config": [
        "config_{env}",
        "settings_{env}",
        "parameters_{env}",
        "options_{env}",
        "preferences_{env}",
        "properties_{env}",
    ],
}

# File extensions by directory type (with weights - higher = more common)
DIRECTORY_FILE_TYPES = {
    "documents": [
        (".txt", 30),
        (".md", 20),
        (".pdf", 10),
        (".docx", 5),
        (".log", 15),
        (".csv", 10),
        (".json", 10),
    ],
    "src": [
        (".py", 20),
        (".js", 20),
        (".java", 15),
        (".cpp", 10),
        (".h", 10),
        (".json", 10),
        (".yml", 10),
        (".yaml", 5),
    ],
    "data": [
        (".json", 20),
        (".csv", 20),
        (".bin", 20),
        (".dat", 15),
        (".tmp", 10),
        (".cache", 10),
        (".png", 5),
        (".jpg", 5),
        (".mp3", 3),
        (".mp4", 2),
    ],
    "config": [
        (".json", 30),
        (".yaml", 25),
        (".yml", 25),
        (".ini", 10),
        (".toml", 10),
    ],
    "default": [
        (".txt", 30),
        (".md", 20),
        (".json", 20),
        (".log", 15),
        (".csv", 15),
    ],
}

# All available file extensions (for root and other general files)
ALL_FILE_EXTENSIONS = [
    ".txt",
    ".md",
    ".log",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".html",
    ".sql",
    ".csv",
    ".java",
    ".cpp",
    ".h",
    ".bin",
    ".dat",
    ".png",
    ".jpg",
    ".mp3",
    ".mp4",
]

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


def generate_random_filename(dir_type: str, counter: int) -> str:
    """Generate a random filename based on directory type."""
    templates = FILE_NAME_TEMPLATES.get(dir_type, FILE_NAME_TEMPLATES["documents"])
    template = random.choice(templates)

    # Replace placeholders
    filename = template
    if "{year}" in filename:
        filename = filename.replace("{year}", str(random.randint(2020, 2024)))
    if "{month}" in filename:
        filename = filename.replace("{month}", f"{random.randint(1, 12):02d}")
    if "{date}" in filename:
        filename = filename.replace("{date}", f"{random.randint(1, 31):02d}_{random.randint(1, 12):02d}")
    if "{num}" in filename:
        filename = filename.replace("{num}", f"{counter:03d}")
    if "{env}" in filename:
        env = random.choice(["dev", "prod", "staging", "test", "qa", "uat"])
        filename = filename.replace("{env}", env)

    # Choose extension
    ext_weights = DIRECTORY_FILE_TYPES.get(dir_type, DIRECTORY_FILE_TYPES["default"])
    extensions = [ext for ext, weight in ext_weights for _ in range(weight)]
    extension = random.choice(extensions)

    return filename + extension


def generate_general_filename(counter: int) -> str:
    """Generate a general filename for root or mixed directories."""
    prefixes = [
        "file",
        "document",
        "note",
        "backup",
        "archive",
        "temp",
        "export",
        "import",
        "log",
        "data",
        "config",
        "settings",
        "cache",
        "session",
        "token",
        "profile",
    ]
    prefix = random.choice(prefixes)
    extension = random.choice(ALL_FILE_EXTENSIONS)
    return f"{prefix}_{counter:03d}{extension}"


def create_random_files(base_path: Path, target_count: int, existing_count: int) -> int:
    """Create additional random files to reach target count."""
    file_count = existing_count
    max_attempts = (target_count - existing_count) * 3  # 防止无限循环
    attempts = 0

    # Get all directories in the structure
    all_dirs = [str(p.relative_to(base_path)) for p in base_path.rglob("*") if p.is_dir()]
    if not all_dirs:
        all_dirs = ["."]

    while file_count < target_count and attempts < max_attempts:
        attempts += 1

        # Choose a random directory
        rel_dir = random.choice(all_dirs)
        dir_path = base_path / rel_dir

        # Determine directory type for file generation
        dir_type = "default"
        if "documents" in rel_dir:
            dir_type = "documents"
        elif "src" in rel_dir or "lib" in rel_dir or "components" in rel_dir:
            dir_type = "src"
        elif "data" in rel_dir:
            dir_type = "data"
        elif "config" in rel_dir:
            dir_type = "config"

        # Generate filename
        if rel_dir == ".":
            filename = generate_general_filename(file_count + 1)
        else:
            filename = generate_random_filename(dir_type, file_count + 1)

        file_path = dir_path / filename

        # Skip if file already exists
        if file_path.exists():
            continue

        # Create the file
        ext = file_path.suffix.lower()
        generator = FILE_GENERATORS.get(ext, create_text_file)

        try:
            generator(file_path)
            file_count += 1
            if file_count % 10 == 0:
                print(f"  Progress: {file_count}/{target_count} files created...")
        except Exception as e:
            print(f"  Warning: Failed to create {file_path}: {e}")
            continue

    return file_count


def create_root_files(base_path: Path) -> int:
    """Create some files in the root directory."""
    root_files = [
        "README.md",
        "config.json",
        ".gitignore",
        "LICENSE",
        "requirements.txt",
        "package.json",
        "Dockerfile",
        ".env.example",
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
*.tmp
.cache/
dist/
build/
""",
                encoding="utf-8",
            )
        elif filename == "LICENSE":
            file_path.write_text(
                """MIT License

Copyright (c) 2024 Test Project

Permission is hereby granted...
""",
                encoding="utf-8",
            )
        elif filename == "requirements.txt":
            file_path.write_text(
                """textual>=0.47.0
pydantic>=2.0.0
oss2>=2.18.0
pytest>=8.0.0
""",
                encoding="utf-8",
            )
        elif filename == "package.json":
            file_path.write_text(
                """{
  "name": "test-project",
  "version": "1.0.0",
  "description": "A test project",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "start": "node index.js"
  }
}
""",
                encoding="utf-8",
            )
        elif filename == "Dockerfile":
            file_path.write_text(
                """FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "app.py"]
""",
                encoding="utf-8",
            )
        elif filename == ".env.example":
            file_path.write_text(
                """# Environment variables
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
API_KEY=your_api_key_here
""",
                encoding="utf-8",
            )
        else:
            generator = FILE_GENERATORS.get(ext, create_text_file)
            generator(file_path)

        file_count += 1
        print(f"  Created: {filename}")

    return file_count


def generate_test_directory(
    output_path: str | Path,
    seed: int | None = None,
    target_file_count: int = 150,
) -> None:
    """Generate a complete test directory structure.

    Args:
        output_path: Path where the test directory will be created.
        seed: Random seed for reproducible generation.
        target_file_count: Target number of files to create (100-200 recommended).
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

    print(f"\n{'=' * 60}")
    print(f"Generating test directory at: {base_path.absolute()}")
    print(f"Target file count: {target_file_count}")
    print(f"{'=' * 60}\n")

    # Create directory structure
    print("Creating directory structure...")
    base_path.mkdir(parents=True, exist_ok=True)
    create_directory_structure(base_path, DIRECTORY_STRUCTURE)
    print("  Directory structure created.\n")

    # Create files
    print("Creating fixed files...")
    file_count = create_root_files(base_path)
    file_count += create_files(base_path)
    print(f"  Created {file_count} fixed files.\n")

    # Create additional random files if needed
    if file_count < target_file_count:
        additional_needed = target_file_count - file_count
        print(f"Creating {additional_needed} additional random files...")
        file_count = create_random_files(base_path, target_file_count, file_count)
        print()

    # Summary
    print(f"{'=' * 60}")
    print("Test directory generated successfully!")
    print(f"  Location: {base_path.absolute()}")
    print(f"  Total files created: {file_count}")

    # Count directories
    dir_count = sum(1 for _ in base_path.rglob("*") if _.is_dir())
    print(f"  Total directories: {dir_count}")

    # Calculate average files per directory
    avg_files = file_count / dir_count if dir_count > 0 else 0
    print(f"  Average files per directory: {avg_files:.1f}")

    # Show file type distribution
    ext_counts = {}
    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

    print(f"  File type distribution (top 5):")
    sorted_exts = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_exts[:5]:
        percentage = (count / file_count) * 100
        print(f"    {ext or 'no ext'}: {count} files ({percentage:.1f}%)")

    print(f"{'=' * 60}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a test directory structure for OSS testing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Create in ./test_data with ~150 files
  %(prog)s -o /tmp/oss_test         # Create in /tmp/oss_test
  %(prog)s --seed 42                # Use fixed seed for reproducibility
  %(prog)s --file-count 200         # Create exactly 200 files
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
    parser.add_argument(
        "--file-count",
        type=int,
        default=150,
        help="Target number of files to create (default: 150, recommended: 100-200)",
    )

    args = parser.parse_args()
    generate_test_directory(args.output, args.seed, args.file_count)


if __name__ == "__main__":
    main()
