"""This module adds color to text in shell.

The color choices are based on text contexts:
- Error: red
- Info: blue
- OK: green
- Warning: yellow
- Highlight: cyan

Usage example:
    info = get_info('some text here')
"""

class TextColor():
    """Prefixes and suffixes of colored texts."""
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'


def get_error(message: str) -> str:
    """Wraps text with color codes to represent an error message."""
    return TextColor.RED + _add_suffix(message)


def get_info(message: str) -> str:
    """Wraps text with color codes to represent an info message."""
    return TextColor.BLUE + _add_suffix(message)


def get_ok(message: str) -> str:
    """Wraps text with color codes to represent an OK message."""
    return TextColor.GREEN + _add_suffix(message)


def get_highlight(message: str) -> str:
    """Wraps text with color codes to represent an highlight message."""
    return TextColor.CYAN + _add_suffix(message)


def get_warning(message: str) -> str:
    """Wraps text with color codes to represent a warning message."""
    return TextColor.YELLOW + _add_suffix(message)


def _add_suffix(message: str) -> str:
    return message + TextColor.ENDC
