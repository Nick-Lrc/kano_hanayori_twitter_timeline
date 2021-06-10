"""This module handles file IO.

Supported file format(s):
- JSON

Usage example:
    input = load_json('path/to/input')
    dump_json(input, 'path/to/output')
"""

import json
import os


def dump_json(obj: dict, path: str, sorted_keys: bool = True) -> None:
    """Dumps a dictionary to a JSON file with utf-8 encoding."""
    with open(os.path.normpath(path), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4, sort_keys=sorted_keys)


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