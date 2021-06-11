"""This module handles string operations."""

def replace_last(text: str, target: str) -> str:
    """Replaces the last occurrence of target."""
    parts = text.rpartition(target)
    return parts[0] + parts[-1]
