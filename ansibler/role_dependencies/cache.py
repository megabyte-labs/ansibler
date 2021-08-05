import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, List, Optional
from ruamel.yaml import YAML
from ansibler.utils.files import create_folder_if_not_exists, list_files
from ansibler.exceptions.ansibler import MetaYMLError
from ansibler.utils.files import create_folder_if_not_exists
from ansibler.role_dependencies.role_info import get_role_name


META_FILES_PATTERN = "**/meta/main.yml"
CACHE_MAP_DIR = str(Path.home()) + "/.local/megabytelabs/ansibler/"
CACHE_MAP_FILE = "role_metadata"


def read_roles_metadata_from_cache() -> Dict[str, Any]:
    # TODO: TESTS
    try:
        cache = None
        with open(CACHE_MAP_DIR + CACHE_MAP_FILE) as f:
            cache = json.load(f)
        if not cache:
            return None
        print(f"Read cache from {CACHE_MAP_DIR}{CACHE_MAP_FILE}")
    except (FileNotFoundError, JSONDecodeError):
        pass

    return cache


def cache_roles_metadata(
    roles_path: List[str],
    current_cache: Optional[Dict[str, Any]] = {}
) -> Dict[str, Any]:
    # TODO: TESTS
    # Create cache folder if it does not exist
    create_folder_if_not_exists(CACHE_MAP_DIR)

    cache = {**current_cache}

    for role_path in roles_path:
        meta_files = list_files(role_path, META_FILES_PATTERN, True)

        for meta_file in meta_files:
            meta_file_path = meta_file[0]
            role_name = get_role_name(role_path, meta_file_path)

            try:
                cache_single_role_metadata(
                    meta_file_path, role_path, role_name, cache)
            except:
                pass

    with open(CACHE_MAP_DIR + CACHE_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print("Role metadata cached")
    return cache


def cache_single_role_metadata(
    meta_file_path: str, role_path: str, role_name: str, cache: Dict[str, Any]
) -> None:
    # TODO: TESTS
    # Read and parse meta/main.yml
    data = {}
    with open(meta_file_path) as f:
        yaml = YAML()
        data = yaml.load(f)

    err_msg = f"Invalid meta/main.yml in: {role_path}"
    if not role_path.endswith("/"):
        err_msg += "/"
    err_msg += role_name

    if data is None:
        print(err_msg)
        raise MetaYMLError(err_msg)

    # Read galaxy_info
    galaxy_info = data.get("galaxy_info", {})

    # Raise exceptions if invalid meta/main.yml
    if not galaxy_info:
        print(err_msg)
        raise MetaYMLError(err_msg)

    if "role_name" not in galaxy_info or \
        "author" not in galaxy_info or \
        "description" not in galaxy_info:
        print(err_msg)
        raise MetaYMLError(err_msg)

    # Build cache map for this single role
    metadata = {
        "role_name": galaxy_info.get("role_name"),
        "namespace": galaxy_info.get("author"),
        "description": galaxy_info.get("description"),
        "platforms": galaxy_info.get("platforms", []),
        "repository": galaxy_info.get("repository", None),
        "repository_status": galaxy_info.get("repository_status", None)
    }

    # Append to cache
    cache[role_name] = metadata


def append_role_to_cache(
    role_name: str, metadata: str, cache: Dict[str, Any]
) -> None:
    # TODO: TESTS
    # Append to cache
    cache[role_name] = metadata

    # Rewrite cache
    with open(CACHE_MAP_DIR + CACHE_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def clear_cache() -> None:
    """
    Clears ansibler cache
    """
    # TODO: TESTS
    Path(CACHE_MAP_DIR + CACHE_MAP_FILE).unlink(missing_ok=True)
