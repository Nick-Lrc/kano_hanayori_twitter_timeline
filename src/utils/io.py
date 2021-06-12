"""This module handles file IO."""

import json
import os
import shutil


def add_suffix(path: str, suffix: str) -> str:
    """Adds a suffix to the path before the last extension."""
    norm_path, ext = os.path.splitext(os.path.normpath(path))
    return norm_path + suffix + ext


def has_suffix(path: str, suffix: str) -> str:
    """Checks if the path has the suffix."""
    return get_filename(path).endswith(suffix)


def archive_file(path: str, archive: str = 'arc') -> str:
    """Archives the file by copying it into the given directory."""
    if not os.path.isfile(path):
        raise OSError(f'{path} is not a file.')

    src = os.path.normpath(path)
    parent = os.path.dirname(src)
    filename = os.path.basename(src)
    archive_path = os.path.normpath(os.path.join(parent, archive))
    make_directory(archive_path)
    dst = os.path.join(archive_path, filename)
    shutil.copy(src, dst)
    return dst


def dump_json(obj: dict, path: str, sorted_keys: bool = True) -> None:
    """Dumps a dictionary to a JSON file with utf-8 encoding."""
    with open(os.path.normpath(path), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4, sort_keys=sorted_keys)


def get_extension(path: str) -> str:
    """Extracts the file extension."""
    return os.path.splitext(os.path.normpath(path))[-1]


def get_filename(path: str) -> str:
    """Extracts the filename without extension."""
    return os.path.splitext(os.path.normpath(path))[0]


def load_json(path: str) -> dict:
    """Loads a JSON file with utf-8 encoding into a dictionary."""
    with open(os.path.normpath(path), 'r', encoding='utf-8') as f:
        return json.load(f)


def join_paths(parent: str, child: str) -> str:
    """Joins the parent and child paths together."""
    return os.path.normpath(os.path.join(parent, child))


def make_directory(path: str) -> str:
    """Creates the directory and its parents if necessary."""
    os.makedirs(os.path.normpath(path), exist_ok=True)


def replace_extension(path: str, extension: str) -> str:
    """Replaces the old extension with the new one."""
    return get_filename(path) + extension
