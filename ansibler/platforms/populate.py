import json
from typing import Any, Dict
import yaml
from yaml.error import YAMLError
from yaml.loader import SafeLoader
from yaml.dumper import SafeDumper
from ansibler.utils.files import create_file_if_not_exists, create_folder_if_not_exists


def populate_platforms() -> None:
    # TODO: TESTS
    package_json_path = "./package.json"

    # Read from package.json
    package = read_package_json(package_json_path)
    blueprint = package.get("blueprint", {})
    compatibility = blueprint.get("compatibility", [])
    compatibility = [] if len(compatibility) <= 1 else compatibility[1:]

    # Generate platforms value
    platforms = [
        {
            "name": platform[0],
            "versions": [
                "all" if platform[0].lower() == "windows" else platform[1]
            ]
        }
        for platform in compatibility
    ]

    # Populate meta/main.yml
    meta_main = read_meta_main("./meta/main.yml")
    galaxy_info = meta_main.get("galaxy_info", {})
    galaxy_info["platforms"] = platforms if platforms else None
    meta_main["galaxy_info"] = galaxy_info

    # Save
    create_folder_if_not_exists("./meta/")
    with open("./meta/main.yml.ansibler", "w") as f:
        yaml.dump(meta_main, f, Dumper=SafeDumper)

    print("Done")


def read_package_json(package_json_path: str) -> Dict[str, Any]:
    # TODO: TESTS
    with open(package_json_path) as f:
        return json.load(f)


def read_meta_main(meta_main_path: str) -> Dict[str, Any]:
    # TODO: TESTS
    try:
        with open(meta_main_path) as f:
            return yaml.load(f, Loader=SafeLoader)
    except (FileNotFoundError, YAMLError):
        return {}
