"""This module handles string operations."""

from datetime import datetime


def convert_timestamp(timestamp: str, in_format: str, out_format: str) -> str:
    """Convert the timestamp to a new format."""
    return datetime.strptime(timestamp, in_format).strftime(out_format)


def remove_last(text: str, target: str) -> str:
    """Removes the last occurrence of target."""
    parts = text.rpartition(target)
    return parts[0] + parts[-1]


def replace_first(text: str, old: str, new: str) -> str:
    """Replaces the first occurence of the old token with the new one."""
    return text.replace(old, new, 1)
