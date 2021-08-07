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


def create_file_if_not_exists(path: str) -> None:
    """
    Creates file if it does not exist.

    Args:
        path (str): file path
    """
    # TODO: TESTS
    pathlib.Path(path).touch(exist_ok=True)


def check_folder_exists(path: str) -> bool:
    """
    Checks if a directory exists

    Args:
        path (str): dir

    Returns:
        bool: exists
    """
    return pathlib.Path(path).is_dir()


def check_file_exists(path: str) -> bool:
    """
    Checks if a file exists

    Args:
        path (str): file path

    Returns:
        bool: exists
    """
    # TODO: TESTS
    return pathlib.Path(path).is_file()


def list_files(
    path: str,
    pattern: Optional[str] = "*",
    absolute_path: Optional[bool] = False
) -> List[Tuple[str, datetime]]:
    """
    Lists files in a directory and returns name, datetime

    Args:
        path (str): dir
        pattern (str): only match files that satisfy this pattern
        absolute_path (bool): indicates whether returned paths should be
        absolute. When it's equal to False, only the file name is returned.

    Returns:
        (List[Tuple[str, date]]): list of file (name, date)
    """
    p = pathlib.Path(path).glob(pattern)
    return [
        (
            x.name if not absolute_path else str(x.resolve()),
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
    """
    Copies file, optionally adds new content.

    Args:
        src (str): src file
        destination (str): destination file
        new_content (str, optional): new content - defaults to None.
        is_json (bool, optional): json file? - defaults to False.

    Raises:
        shutil.SameFileError: raised when src and destination are the same file
    """
    # Create destination folder if it doesnt exist
    parent_dir = pathlib.Path(destination).parents[0]
    create_folder_if_not_exists(parent_dir)

    # Copy file
    try:
        shutil.copy(src, destination)
    except shutil.SameFileError as e:
        # If content is to be overwritten, ignore SameFileError
        if new_content:
            pass
        else:
            raise e

    # Overwrite content if necessary
    if new_content:
        with open(destination, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(
                    json.loads(new_content), f, ensure_ascii=False, indent=2)
            else:
                f.write(new_content)
