import subprocess
from typing import List


def get_subprocess_output(bash_command: List[str]) -> str:
    """
    Runs ansible autodoc.

    Args:
        bash_command (str) = command to run
    """
    output = subprocess.check_output(bash_command, encoding="UTF-8")
    return output.strip()
