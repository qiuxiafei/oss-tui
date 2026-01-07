"""Object data model."""

from datetime import datetime

from pydantic import BaseModel


class Object(BaseModel):
    """Represents a storage object (file or directory)."""

    key: str
    size: int = 0
    last_modified: datetime | None = None
    etag: str | None = None
    content_type: str | None = None
    is_directory: bool = False

    @property
    def name(self) -> str:
        """Get the object name (last part of the key)."""
        return self.key.rstrip("/").split("/")[-1]


class ListObjectsResult(BaseModel):
    """Result of list_objects operation with pagination support."""

    objects: list[Object]
    is_truncated: bool = False
    next_marker: str | None = None
