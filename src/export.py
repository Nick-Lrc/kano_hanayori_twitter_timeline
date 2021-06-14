"""This scripts exports the webpage along with data and styles to the destination.

The default
- Relative path to the project root directory is '..'.
- Export requirements file locates at 'configs/export.json'.
- Media settings file locates at 'configs/media.json'.
- Export destination is '../../kano_hanayori_twitter'.

Example usage:
    python export.py \
        -i "path/to/the/project/root/directory" \
        -r "path/to/the/export/requirements/config/file" \
        -s "path/to/the/media/config/file" \
        -x "path/to/the/export/destination"
"""

import argparse
import os
import shutil
from typing import Callable

from utils import color, io # pylint: disable=import-error


def export_media_directory(
        dirname: str, base: str, export: str, overwrite: bool, ignored: set, 
        use_remote_video: bool, video_exts: set, img_exts: set) -> None:
    """Export files in the media directory to the destination.

    Parameters
    ----------
    dirname: str
        Directory name without parent (directories).
    base: str
        Path to the project root directory.
    export: str
        Path to the export destination directory.
    overwrite: bool
        Whether or not to overwrite files in the export destination directory.
    ignored: set
        Directory names to ignore.
    use_remote_video: bool
        Whether or not to map video files to their remote URLs instead of their
        local paths.
    video_exts: set
        Set of acceptable video extensions.
    img_exts: set
        Set of acceptable image extensions.
    condition: Callable[[str], bool], default: lambda filename: True
        Condition check before file export.
    """
    def _is_media_required(filename: str) -> bool:
        ext = io.get_extension(filename)
        return ext in img_exts or (not use_remote_video and ext in video_exts)

    return export_directory(
        dirname, base, export, overwrite, ignored, condition=_is_media_required)


def export_directory(
        dirname: str, base: str, export: str, overwrite: bool, ignored: set,
        condition: Callable[[str], bool] = lambda filename: True) -> None:
    """Export files in the directory to the destination.

    Parameters
    ----------
    dirname: str
        Directory name without parent (directories).
    base: str
        Path to the project root directory.
    export: str
        Path to the export destination directory.
    overwrite: bool
        Whether or not to overwrite files in the export destination directory.
    ignored: set
        Directory names to ignore.
    condition: Callable[[str], bool], default: lambda filename: True
        Condition check before file export.
    """
    for root, _, files in os.walk(io.join_paths(base, dirname)):
        if _required_directory(root, ignored):
            for file in files:
                src = os.path.join(root, file)
                filename = io.remove_parent(src, base)
                if condition(filename):
                    export_file(filename, base, export, overwrite)


def export_file(filename: str, base: str, export: str, overwrite: bool) -> None:
    """Export the file to the destination.

    Parameters
    ----------
    filename: str
        Filename without parent (directories).
    base: str
        Path to the project root directory.
    export: str
        Path to the export destination directory.
    overwrite: bool
        Whether or not to overwrite files in the export destination directory.
    """
    dst = io.join_paths(export, filename)
    if overwrite or not os.path.isfile(dst):
        io.make_directory(os.path.dirname(dst))
        src = io.join_paths(base, filename)
        print(f'{color.get_highlight(src)} -> ', end='')
        shutil.copyfile(src, dst)
        print(color.get_ok(dst))


def verify_requirements(base: str, requirements: list) -> None:
    """Verify the existence of all required directories and files.
    
    Parameters
    ----------
    base: str
        Path to the project root directory.
    requirements: list
        List of required directories and files.

    Raises
    ------
    FileNotFoundError
        If a required directory or file does not exist.
    """
    for requirement in requirements:
        path = io.join_paths(base, requirement)
        if not os.path.exists(path):
            raise FileNotFoundError(f"ERROR: '{path}' not found.")


def _required_directory(path: str, ignored: set) -> bool:
    for parent in ignored:
        if io.has_parent(path, parent):
            return False
    return True


def _get_options():
    parser = argparse.ArgumentParser(
        description='Exports the webpage with required media.')
    parser.add_argument(
        '-i', '--input', default='..', type=str, 
        help='Path relative to the project root directory.')
    parser.add_argument(
        '-r', '--requirements', default='configs/export.json', type=str, 
        help='Required directories and files to export.')
    parser.add_argument(
        '-s', '--settings', default='configs/media.json', type=str, 
        help='Path to media config file.')
    parser.add_argument(
        '-x', '--export', default='../../kano_hanayori_twitter_test', type=str, 
        help='Path to the export directory.')
    parser.add_argument(
        '--use-remote-video', action='store_true', default=False, 
        help='Exports images only. Set this flag only if the webpage writer '
             'has the same flag.')
    parser.add_argument(
        '--overwrite', action='store_true', default=False, 
        help='Overwrites existing files in the export directory.')
    return parser.parse_args()


if __name__ == '__main__':
    options = _get_options()
    base = options.input
    requirements = io.load_json(options.requirements)
    required = requirements['required']
    required_media = required['media']
    required_dirs = required['directories']
    required_files = required['files']
    verify_requirements(base, [required_media] + required_dirs + required_files)
    ignored = set(requirements['ignored'])
    
    settings = io.load_json(options.settings)
    video_exts = set(settings['video']['extensions'])
    img_exts = set(settings['image']['extensions'])
    export = options.export
    
    print(color.get_info(f"Exporting the project to '{export}'..."))
    export_media_directory(
        required_media, base, export, options.overwrite, ignored,
        options.use_remote_video, video_exts, img_exts)

    for dirname in required_dirs:
        export_directory(dirname, base, export, options.overwrite, ignored)
    for filename in required_files:
        export_file(filename, base, export, options.overwrite)
    print()
    print(color.get_ok('Done.'))
