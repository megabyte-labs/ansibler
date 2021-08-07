import subprocess
from typing import List, Optional


def get_subprocess_output(
    bash_cmd: List[str], filter_by: Optional[str] = None
) -> str:
    """
    Get subprocess output, filters (grep) if necessary.

    Args:
        bash_cmd (List[str]): command to run
        filter_by (str, optional): filter

    Returns:
        str: output
    """
    # Run cmd
    with subprocess.Popen(
        bash_cmd, stdout=subprocess.PIPE, encoding="UTF-8") as ps:

        # Filter
        if filter_by:
            output = subprocess.check_output(
                ("grep", filter_by), stdin=ps.stdout, encoding="UTF-8")
        else:
            output, _ = ps.communicate()

        # Wait for subprocess to terminate, then return output
        ps.wait()
        return output.strip()
