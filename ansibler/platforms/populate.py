import json
from sys import platform
from typing import Any, Dict, List, Optional
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ansibler.utils.files import create_folder_if_not_exists


def populate_platforms(inline_replace: Optional[bool] = False) -> None:
    # TODO: TESTS
    package_json_path = "./package.json"

    # Read from package.json
    package = read_package_json(package_json_path)
    blueprint = package.get("blueprint", {})
    compatibility = blueprint.get("compatibility", [])
    compatibility = [] if len(compatibility) <= 1 else compatibility[1:]

    # Generate platforms value
    platforms, supported, unsupported = [], [], []
    for platform in compatibility:
        os = f"{platform[0]}-{platform[1]}"
        if platform[2] == "✅":
            platforms.append({
                "name": platform[0],
                "versions": [
                    "all" if platform[0].lower() == "windows" else platform[1]
                ]
            })
            supported.append(os)
        else:
            unsupported.append(os)

    # Populate meta/main.yml
    meta_main = read_meta_main("./meta/main.yml")
    galaxy_info = meta_main.get("galaxy_info", {})

    old_platforms = galaxy_info.get("platforms", [])
    platforms = merge_platforms(
        platforms, old_platforms, supported, unsupported)

    galaxy_info["platforms"] = platforms if platforms else None
    meta_main["galaxy_info"] = galaxy_info

    # Save
    create_folder_if_not_exists("./meta/")
    out = "./meta/main.yml" if inline_replace else "./meta/main.ansibler.yml"
    with open(out, "w") as f:
        yaml = YAML()
        yaml.explicit_start = True
        yaml.dump(meta_main, f)

    print("Done")


def read_package_json(package_json_path: str) -> Dict[str, Any]:
    # TODO: TESTS
    with open(package_json_path) as f:
        return json.load(f)


def read_meta_main(meta_main_path: str) -> Dict[str, Any]:
    # TODO: TESTS
    try:
        with open(meta_main_path) as f:
            yaml = YAML()
            return yaml.load(f)
    except (FileNotFoundError, YAMLError):
        return {}


def merge_platforms(
    current_platforms: List[Dict[str, Any]],
    old_platforms: List[Dict[str, Any]],
    supported: List[str],
    unsupported: List[str]
) -> List[Dict[str, Any]]:
    """
    Merge platforms from package.json's blueprint.compatibility and
    meta/main.yml. Only removes a platform when / if it's marked as unsuccessful
    in the blueprint.compatibility field.

    Args:
        current_platforms (List[Dict[str, Any]]): current platforms data
        old_platforms (List[Dict[str, Any]]): old platforms data
        supported (List[Dict[str, Any]]): supported OSes ({name}-{version})
        unsupported (List[Dict[str, Any]]): unsupported OSes ({name}-{version})

    Returns:
        List[Dict[str, Any]]: merged platforms
    """
    # TODO: TESTS
    res = current_platforms[:]

    for old_platform in old_platforms:
        name = old_platform.get("name", None)
        versions = old_platform.get("versions", [])

        if name is None:
            continue

        for version in versions:
            os = f"{name}-{version}"
            added = False

            if os not in unsupported and os not in supported:
                for current_platform in res:
                    cur_name = current_platform.get("name")
                    if cur_name == name:
                        cur_versions = current_platform.get("versions", [])
                        cur_versions.append(version)
                        supported.append(os)
                        added = True

                if not added:
                    res.append({"name": name, "versions": [version]})
                    supported.append(os)

    return res
