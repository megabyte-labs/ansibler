import re
import json
from typing import Any, Dict, List
import yaml
from yaml.loader import SafeLoader
from ansibler.utils.subprocesses import get_subprocess_output
from ansibler.utils.files import create_folder_if_not_exists, list_files
from ansibler.exceptions.ansibler import (
    CommandNotFound, RolesParseError, MetaYMLError
)


ROLES_PATTERN = r"\[.*\]"
META_FILES_PATTERN = "**/meta/main.yml"
CACHE_MAP_DIR = "~/.local/megabytelabs/ansibler/"
CACHE_MAP_FILE = "role_metadata"


def generate_role_dependency_chart() -> None:
    pass


def get_default_roles() -> str:
    # Get default roles
    bash_cmd = ["ansible-config", "dump", "|", "grep", "DEFAULT_ROLES_PATH"]
    default_roles = get_subprocess_output(bash_cmd)

    # Check if valid
    if "DEFAULT_ROLES_PATH" not in default_roles:
        raise CommandNotFound(f"Could not run {' '.join(bash_cmd)}")

    return default_roles


def parse_default_roles(default_roles: str) -> List[str]:
    # Find list of roles
    match = re.search(ROLES_PATTERN, default_roles)
    if not match:
        raise RolesParseError(f"Couldn't parse roles from: {default_roles}")

    # Parse them
    roles = match.group(0).strip("[").strip("]").replace("'", "").split(",")
    return roles


def cache_roles_metadata(roles_path: List[str]) -> None:
    # Create cache folder if it does not exist
    create_folder_if_not_exists(CACHE_MAP_DIR)

    cache = {}

    for role_path in roles_path:
        meta_files = list_files(role_path, META_FILES_PATTERN, True)

        for meta_file in meta_files:
            meta_file_path = meta_file[0]
            role_name = get_role_name(role_path, meta_file_path)

            cache_single_role_metadata(
                meta_file_path, role_path, role_name, cache)

    with open(CACHE_MAP_DIR + CACHE_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print("Role metadata cached")


def get_role_name(role_path: str, meta_file_path: str) -> str:
    return meta_file_path \
        .replace("meta/main.yml", "") \
        .replace(role_path, "") \
        .strip("/", "")


def get_role_full_path(role_path: str, role_name: str) -> str:
    if role_path.endswith("/"):
        role_full_path = role_path
    else:
        role_full_path = role_path + "/"

    role_full_path += role_name

    return role_full_path


def cache_single_role_metadata(
    meta_file_path: str, role_path: str, role_name: str, cache: Dict[str, Any]
) -> None:
    data = {}

    with open(meta_file_path) as f:
        data = yaml.load(f, Loader=SafeLoader)

    # Build cache map for this single role
    galaxy_info = data.get("galaxy_info", None)
    if not galaxy_info:
        raise MetaYMLError(f"Invalid meta/main.yml in: {role_path}/{role_name}")

    if "role_name" not in galaxy_info or \
        "author" not in galaxy_info or \
        "description" not in galaxy_info:
        raise MetaYMLError(f"Invalid meta/main.yml in: {role_path}/{role_name}")

    metadata = {
        "role_name": galaxy_info.get("role_name"),
        "namespace": galaxy_info.get("author"),
        "description": galaxy_info.get("description"),
    }

    cache[role_path][role_name] = metadata
