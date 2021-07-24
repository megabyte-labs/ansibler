import pathlib
import shutil
import json
from datetime import datetime
from typing import List, Optional, Tuple


def create_folder_if_not_exists(path: str) -> None:
    """
    Creates dir if it does not exist.

    Args:
        path (str): dir
    """
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def check_folder_exists(path: str) -> bool:
    """
    Checks if a directory exists

    Args:
        path (str): dir

    Returns:
        bool: [description]
    """
    return pathlib.Path(path).is_dir()


def list_files(
    path: str,
    pattern: Optional[str] = "*",
    full_filepath: Optional[bool] = False
) -> List[Tuple[str, datetime]]:
    """
    Lists files in a directory and returns name, datetime

    Args:
        path (str): dir
        pattern (str): only match files that satisfy this pattern
        full_filepath (bool): indicates whether returned paths should include
        parent dirs. When it's equal to True, the file name is returned.

    Returns:
        (List[Tuple[str, date]]): list of file (name, date)
    """
    p = pathlib.Path(path).glob(pattern)
    return [
        (
            x.name if not full_filepath else str(x),
            datetime.fromtimestamp(x.stat().st_ctime)
        )
        for x in p
        if x.is_file()
    ]


def copy_file(
    src: str,
    destination: str,
    new_content: Optional[str] = None,
    is_json: Optional[bool] = False
) -> None:
    # Create destination folder if it doesnt exist
    parent_dir = pathlib.Path(destination).parents[0]
    create_folder_if_not_exists(parent_dir)

    # Copy file
    shutil.copy(src, destination)

    # Overwrite content if necessary
    if new_content:
        with open(destination, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(
                    json.loads(new_content), f, ensure_ascii=False, indent=2)
            else:
                f.write(new_content)
