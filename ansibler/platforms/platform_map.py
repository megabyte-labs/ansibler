import json
from typing import Any, Dict, List, Optional
from ansibler.utils.files import check_file_exists


def parse_platform_map(
    platform_map_file: Optional[str] = None
) -> Dict[str, str]:
    # Check if valid file
    if not platform_map_file or not check_file_exists(platform_map_file):
        return {}

    # Parse (should be json)
    parsed_platform_map = {}
    with open(platform_map_file) as f:
        try:
            parsed_platform_map = json.loads(f.read())
        except:
            print("Invalid platform map (make sure it's JSON)")
            parsed_platform_map = {}

    return parsed_platform_map


def map_to_galaxy_supported_platforms(
    platforms: List[Dict[str, Any]], platform_map: Dict[str, str]
) -> List[Dict[str, Any]]:
    mapped_platforms = {}

    for platform in platforms:
        name = platform.get("name", None)

        if name:
            for version in platform.get("versions", []):
                # Value to map
                key = f"{name}-{str(version)}"

                # Mapped value
                value = platform_map.get(key, key).split("-", 1)

                # New values
                mapped_os, mapped_release  = value[0], value[1]

                # Append to mapped platforms
                current_versions = mapped_platforms.get(mapped_os, [])
                if mapped_release not in current_versions:
                    current_versions.append(
                        get_formatted_version(mapped_release))
                mapped_platforms[mapped_os] = current_versions

    return [
        {"name": os, "versions": versions}
        for os, versions in mapped_platforms.items()
    ]


def get_formatted_version(version: str):
    try:
        if "." not in version:
            return int(version)

        try:
            return float(version)
        except:
            return int(version)
    except:
        return version
