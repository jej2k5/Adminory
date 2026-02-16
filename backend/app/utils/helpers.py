"""Helper utility functions."""
import uuid
from typing import Optional
from datetime import datetime


def generate_uuid() -> str:
    """
    Generate a new UUID.

    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())


def slugify(text: str) -> str:
    """
    Convert text to slug format.

    Args:
        text: Text to slugify

    Returns:
        str: Slugified text
    """
    import re

    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def utcnow() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        datetime: Current UTC datetime
    """
    return datetime.utcnow()


def parse_boolean(value: Optional[str]) -> bool:
    """
    Parse string to boolean.

    Args:
        value: String value

    Returns:
        bool: Boolean value
    """
    if value is None:
        return False
    return value.lower() in ("true", "1", "yes", "on")
