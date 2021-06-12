"""This module contains HTML utilities."""

import os


def normalize_path(path: str) -> str:
    """Makes the path HTML readable."""
    return '/'.join(os.path.normpath(path).split(os.sep))