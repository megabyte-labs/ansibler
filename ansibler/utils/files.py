import json
import glob
from pathlib import Path
import shutil
from datetime import datetime
from typing import AnyStr, List, Optional, Tuple, Union


def create_folder_if_not_exists(path: str) -> None:
    """
    Creates dir if it does not exist.

    Args:
        path (str): dir
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def create_file_if_not_exists(path: str) -> None:
    """
    Creates file if it does not exist.

    Args:
        path (str): file path
    """
    # TODO: TESTS
    Path(path).touch(exist_ok=True)


def check_folder_exists(path: str) -> bool:
    """
    Checks if a directory exists

    Args:
        path (str): dir

    Returns:
        bool: exists
    """
    return Path(path).is_dir()


def check_file_exists(path: str) -> bool:
    """
    Checks if a file exists

    Args:
        path (str): file path

    Returns:
        bool: exists
    """
    # TODO: TESTS
    return Path(path).is_file()


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
    p = Path(path).glob(pattern)
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
    parent_dir = Path(destination).parents[0]
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


def read_gitignore(gitignore_dir: Optional[str] = "./.gitignore") -> List[str]:
    """
    Read all files to ignore (from .gitignore)

    Args:
        gitignore_dir (str): gitignore's path. Defaults to './.gitignore'

    Returns:
        List[str]: files to ignore
    """
    files_to_ignore = []

    if not check_file_exists(gitignore_dir):
        return files_to_ignore

    for p in Path(gitignore_dir).read_text().split("\n"):
        if p and not p.startswith("#"):
            walk_gitignore(p, files_to_ignore)

    return files_to_ignore


def walk_gitignore(p: Union[Path, str], files_to_ignore: List[str]) -> None:
    """
    Reads a gitignore entry and appends it to the files_to_ignore list. If it is
    a directory, it will make sure to add all of their files and subdirs to the
    list as well.

    Args:
        p (Union[Path, str]): 
        files_to_ignore (List[str]): list of files
    """
    p_path = Path(p)

    if p_path.is_file():
        files_to_ignore.append(p_path.resolve())
    elif p_path.is_dir():
        if p.endswith("/") or p.endswith("\\"):
            files_to_ignore.extend([
                Path(to_ignore).resolve()
                for to_ignore in glob.glob(p + "*")
            ])
        else:
            files_to_ignore.extend([
                Path(to_ignore).resolve()
                for to_ignore in glob.glob(p + "/*")
            ])
    else:
        for subdir in glob.glob(p):
            walk_gitignore(subdir, files_to_ignore)
