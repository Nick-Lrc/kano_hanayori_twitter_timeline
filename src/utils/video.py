"""This module handles operations over video files."""

from datetime import datetime, timedelta
import re

import io, shell # pylint: disable=import-error


def create_thumbnail(src: str, dst: str, cutoff: float) -> None:
    """Creates a video thumbnail.

    Parameters
    ----------
    src: str
        Path to the video file.
    dst: str
        Path to the thumbnail file.
    cutoff: float
        Specifies the video position to get the thumbnail.

    Raises
    ------
    ChildProcessError
        If the FFmpeg fails to extract the thumbnail.
    """
    # Time unit format: '%H:%M:%S.%f'
    thumbnail_position = str(get_duration(src) * cutoff)

    # Note that the '-an' and '-ss' flags are used as input options (before -i).
    result = shell.run([
        'ffmpeg',
        '-an', # Blocks all audio streams of the input file.
        '-hide_banner', # Suppresses printing banner.
        '-loglevel', # Sets logging level and flags.
        'error', # Shows all errors.
        '-ss', # Seeks in the input file to a position.
        thumbnail_position,
        '-y', # Overwrites output files without asking.
        '-i', # Input file url.
        src,
        '-frames:v', # Sets the number of video frames to output. 
        '1', # One frame for the thumbnail. Must be a str (not int) here.
        dst
    ])

    if result.returncode:
        raise ChildProcessError(result.stderr)


def get_duration(path: str) -> timedelta:
    """Gets the video duration.

    Parameters
    ----------
    path: str
        Path to the video file.

    Returns
    -------
    timedelta
        Video duration.

    Raises
    ------
    LookupError
        If fails to get the 'Duration' field from the video info dumped by
        the FFmpeg.
    """
    # FFmpeg returns video info if no output path is spcified.
    result = shell.run([
        'ffmpeg',
        '-i', # Input file
        path
    ])

    info = result.stderr.split('\n')
    for line in info:
        line = line.strip()
        if line.startswith('Duration'):
            # e.g. Duration: 00:01:13.70, start: 0.000000, bitrate: 839 kb/s
            hours, minutes, seconds, milliseconds = re.split(
                r'[:,\.]\s?', line)[1:5]
            return timedelta(
                hours=int(hours), minutes=int(minutes), seconds=int(seconds), 
                microseconds=int(milliseconds) * 1000)
    raise LookupError(f"Duration of '{path}' not found.")
