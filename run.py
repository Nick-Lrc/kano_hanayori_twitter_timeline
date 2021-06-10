"""This script runs all child scripts in sequence.

The default script config file locates at 'src/configs/scripts.json'.

Usage example:
    python run.py -i "path/to/script/config/file"
"""

import argparse
import os
import sys

from src.utils import color, io, shell


def _get_options() -> dict:
    parser = argparse.ArgumentParser(description='Runs all scripts.')
    parser.add_argument(
        '-i', '--input', default='src/configs/scripts.json', type=str, 
        help='Path to script config.')
    return parser.parse_args()


def _print_horizontal_bar() -> None:
    print('---')


if __name__ == '__main__':
    options = _get_options()
    commands = io.load_json(options.input)
    print(color.get_info(f'{len(commands)} script(s) to run.'))

    for i, command in enumerate(commands):
        name = command[1]
        _print_horizontal_bar()
        print(f'[{i + 1}/{len(commands)}] Running {name}...')
        _print_horizontal_bar()

        result = shell.run(command, capture_output=False)
        if result.returncode:
            sys.exit(1)

    _print_horizontal_bar()
    print(color.get_ok('All done.'))