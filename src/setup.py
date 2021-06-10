"""This script checks all requirements and installs missing ones if possible.

The default requirement config file locates at 'configs/requirements.json'.

Usage example:
    python setup.py -i "path/to/requirement/config/file"
"""

import argparse
import sys

from utils import color, io, shell # pylint: disable=import-error


def check_programs(programs: list) -> None:
    """Checks program installations and terminates upon missing program."""
    print(color.get_info(f'{len(programs)} program(s) to check.'))

    has_error = False
    for i, program in enumerate(programs):
        [[name, location]] = program.items()
        print(f'({i + 1}/{len(programs)}) Checking {name}...')

        result = shell.run(['which', name])
        if result.returncode:
            message = (
                f'Error: {name} not found. '
                f'Please visit {location} to download.')
            print(color.get_error(message))
            has_error = True
    print()
    if has_error:
        message = 'Failed to find all required programs. Terminated.'
        print(color.get_error(message))
        sys.exit(1)


def install_packages(packages: list) -> None:
    """Install packages and terminates upon installation failure."""
    print(color.get_info(f'{len(packages)} package(s) to install.'))

    has_error = False
    for i, package in enumerate(packages):
        [[name, location]] = package.items()
        print(f'({i + 1}/{len(packages)}) Installing {name}...')

        result = shell.run(['pip', 'install', '-U', location])
        if result.returncode:
            print(color.get_error(result.stderr.strip()))
            has_error = True
    print()
    if has_error:
        print(color.get_error('Failed to install all packages. Terminated.'))
        sys.exit(1)


def _get_options() -> dict:
    parser = argparse.ArgumentParser(
        description='Checks required programs and install packages.')
    parser.add_argument(
        '-i', '--input', default='configs/requirements.json', type=str, 
        help='Path to requirement config.')
    return parser.parse_args()


if __name__ == '__main__':
    options = _get_options()
    requirements = io.load_json(options.input)

    check_programs(requirements['programs'])
    install_packages(requirements['packages'])
    print(color.get_ok('Done.'))