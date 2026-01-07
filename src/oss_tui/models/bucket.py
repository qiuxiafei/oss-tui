"""Bucket data model."""

from datetime import datetime

from pydantic import BaseModel


class Bucket(BaseModel):
    """Represents a storage bucket."""

    name: str
    creation_date: datetime | None = None
    location: str | None = None
