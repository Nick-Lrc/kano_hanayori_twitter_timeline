"""This module handles string operations."""


def remove_last(text: str, target: str) -> str:
    """Removes the last occurrence of target."""
    parts = text.rpartition(target)
    return parts[0] + parts[-1]


def replace_first(text: str, old: str, new: str) -> str:
    """Replaces the first occurence of the old token with the new one."""
    return text.replace(old, new, 1)
