import json
from typing import Any, Dict, List, Optional
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from ansibler.utils.files import create_folder_if_not_exists


def populate_platforms(json_file: Optional[str] = "./ansibler.json") -> None:
    # TODO: TESTS
    # Read from package.json
    data = read_json_file(json_file)
    compatibility = data.get("compatibility_matrix", [])
    compatibility = [] if len(compatibility) <= 1 else compatibility[1:]

    # Generate platforms value
    platforms, supported, unsupported = [], [], []
    for platform in compatibility:
        os = f"{platform[0]}-{platform[1]}"
        if platform[2] == "✅":
            if platform[0].lower() == "windows":
                version = "all"
            elif platform[1].replace(".", "", 1).isnumeric():
                version = float(platform[1])
            else:
                version = platform[1]

            platforms.append({
                "name": platform[0],
                "versions": [version]
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
    platforms = join_platforms(platforms)

    galaxy_info["platforms"] = platforms if platforms else None
    meta_main["galaxy_info"] = galaxy_info

    # Save
    create_folder_if_not_exists("./meta/")
    out = "./meta/main.yml"
    with open(out, "w") as f:
        yaml = YAML()
        yaml.explicit_start = True
        yaml.dump(meta_main, f)

    print("Done")


def read_json_file(json_file_path: str) -> Dict[str, Any]:
    # TODO: TESTS
    with open(json_file_path) as f:
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


def join_platforms(platforms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Joins platform versions.

    Args:
        platforms (List[Dict[str, Any]]): platforms

    Returns:
        List[Dict[str, Any]]: joined platforms
    """
    # TODO: TESTS
    res = []
    added_names = []

    for platform in platforms:
        name = platform.get("name")
        versions = platform.get("versions", [])

        if name not in added_names:
            res.append({"name": name, "versions": versions})
            added_names.append(name)
        else:
            for p in res:
                added_platform_name = p.get("name")
                added_versions = p.get("versions", [])
                if added_platform_name == name:
                    for version in versions:
                        if version not in added_versions:
                            added_versions.append(version)
                            p["versions"] = sorted(
                                added_versions, key=lambda x: str(x))

    return res
