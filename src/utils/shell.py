"""This modules handles interactions with shell."""

import subprocess
from subprocess import CompletedProcess


def run(command: list, capture_output: bool = False) -> CompletedProcess:
    """Executes the shell command with utf-8 encoding.
    
    Parameters
    ----------
    command : list
        A shell command splitted by space.
    capture_output: bool, defulat: False
        Whether to capture and return stdout and stderr strings.

    Returns
    -------
    CompletedProcess
        The execution result including the following attribute:
        - returncode: an integer representing the exit status.
            0 indicates a success while 1 indicates an error.
        If `capture_output=True`, the result will also includes:
        - stdout: stdout string.
        - stderr: stderr string.
    """
    return subprocess.run(
        command, capture_output=capture_output, encoding='utf-8')
