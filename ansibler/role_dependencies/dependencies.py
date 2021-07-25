from json.decoder import JSONDecodeError
import re
import json
from datetime import datetime
from typing import Any, Dict, Iterator, List, Tuple
import yaml
from yaml.loader import SafeLoader
from ansibler.utils.subprocesses import get_subprocess_output
from ansibler.exceptions.ansibler import CommandNotFound, RolesParseError
from ansibler.role_dependencies.role_info import get_role_name_from_req_file
from ansibler.role_dependencies.cache import (
    read_roles_metadata_from_cache, cache_roles_metadata
)
from ansibler.utils.files import (
    create_folder_if_not_exists,
    list_files,
    copy_file,
    check_file_exists,
    create_file_if_not_exists
)


ROLES_PATTERN = r"\[.*\]"


def generate_role_dependency_chart() -> None:
    """
    Generates role dependency charts. Uses caches whenever possible.
    """
    # TODO: TESTS
    role_paths = parse_default_roles(get_default_roles())

    # Read cache
    cache = read_roles_metadata_from_cache()

    # Generate cache if necessary
    if cache is None:
        cache = cache_roles_metadata(role_paths)

    for role_path in role_paths:
        files = list_files(role_path, "**/requirements.yml", True)
        for f in files:
            role_name = get_role_name_from_req_file(role_path, f[0])

            try:
                generate_single_role_dependency_chart(f, role_path, cache)
            except ValueError as e:
                print(
                    f"\tCouldnt generate dependency chart for {role_name}: {e}")

    print("Done")


def get_default_roles() -> str:
    """
    Get raw DEFAULT_ROLES_PATH from running ansible-config dump

    Raises:
        CommandNotFound: raised when command not available

    Returns:
        str: command output
    """
    # Get default roles
    bash_cmd = ["ansible-config", "dump"]
    default_roles = get_subprocess_output(bash_cmd, "DEFAULT_ROLES_PATH")

    # Check if valid
    if not default_roles or "DEFAULT_ROLES_PATH" not in default_roles:
        raise CommandNotFound(f"Could not run {' '.join(bash_cmd)}")

    return default_roles


def parse_default_roles(default_roles: str) -> List[str]:
    """
    Parses default roles from raw command output

    Args:
        default_roles (str): raw roles dump, straight from cmd output

    Raises:
        RolesParseError: default_roles doesnt have the expected format

    Returns:
        List[str]: list of role paths
    """
    # Find list of roles
    match = re.search(ROLES_PATTERN, default_roles)
    if not match:
        raise RolesParseError(f"Couldn't parse roles from: {default_roles}")

    # Parse them
    roles = match.group(0).strip("[").strip("]").replace("'", "").split(",")
    return [role.strip() for role in roles]


def generate_single_role_dependency_chart(
    requirement_file_data: Tuple[str, datetime],
    role_base_path: str,
    cache: Dict[str, Any]
) -> None:
    # TODO: TESTS
    # Get requirements.yml path and the role's name
    req_file = requirement_file_data[0]
    role_name = get_role_name_from_req_file(role_base_path, req_file)

    print(f"Generating role dependency for {role_name}")

    role_dependencies = []

    # Read dependencies
    dependencies = read_dependencies(req_file)
    # If there's at least one dependency, add headers
    if len(dependencies):
        role_dependencies.append([
            "Role Dependency",
            "Description",
            "Supported OSes",
            "Status"
        ])
    else:
        print(f"\tNo dependencies found in {role_name}")

    for dep in dependencies:
        if dep is None:
            print(f"\tFound invalid dependency in {role_name}")
            continue

        dep_name = dep.split(".")[-1]
        print("\tReading dependency", dep_name)
        dependency_metadata = cache.get(dep_name, {})
        role_dependencies.append(
            get_dependency_metadata(dependency_metadata))

    role_path = role_base_path + "/" + role_name + "/"
    bp_dir = role_path + "blueprint.role_dependencies/"

    # create blueprint folder if it does not exist
    create_folder_if_not_exists(bp_dir)

    data = {}
    bp_file = bp_dir + "package.json"
    package_json_file = bp_dir + "package.json"

    if not check_file_exists(package_json_file):
        package_json_file = role_path + "package.json"

    if not check_file_exists(package_json_file):
        package_json_file = bp_dir + "package.json"
        create_file_if_not_exists(package_json_file)

    try:
        with open(package_json_file) as f:
            data = json.load(f)
    except JSONDecodeError:
        data = {}

    data["role_dependencies"] = role_dependencies
    copy_file(package_json_file, bp_file, json.dumps(data), True)

    print(f"\tGenerated role dependency chart for {role_name}!")


def read_dependencies(requirements_file_path: str) -> List[str]:
    """
    Reads a role dependencies from requirements.yml

    Args:
        requirements_file_path (str): requirements.yml path

    Returns:
        List[str]: list of dependency names
    """
    # TODO: TESTS
    data = {}
    with open(requirements_file_path) as f:
        data = yaml.load(f, Loader=SafeLoader)

    if data is None:
        return []

    return [role["name"] for role in data.get("roles", []) if "name" in role]


def get_dependency_metadata(dependency_metadata: Dict[str, Any]) -> List[str]:
    # TODO: TESTS
    return [
        get_role_dependency_link(dependency_metadata),
        get_role_dependency_description(dependency_metadata),
        get_role_dependency_supported_oses(dependency_metadata),
        get_role_dependency_status(dependency_metadata)
    ]


def get_role_dependency_link(metadata: Dict[str, Any]) -> str:
    """
    Returns role dependency link

    Args:
        metadata (Dict[str, Any]): role metadata

    Returns:
        str: role dependency link
    """
    role_name = metadata.get("role_name", None)
    namespace = metadata.get("namespace", None)

    if not namespace or not role_name:
        raise ValueError(
            f"Can not generate dependency link for {namespace}.{role_name}")
    
    return f"<a href=\"https://galaxy.ansible.com/{namespace}/{role_name}\"" \
           f"title=\"{namespace}.{role_name} on Ansible Galaxy\" target=\"_" \
           f"blank\">{namespace}.{role_name}</a>"


def get_role_dependency_description(metadata: Dict[str, Any]) -> str:
    """
    Returns role dependency description.

    Args:
        metadata (Dict[str, Any]): role metadata

    Returns:
        str: description
    """
    description = metadata.get("description")

    if not description:
        f"Can not get description for {metadata.get('role_name', 'role')}"

    return description


def get_role_dependency_supported_oses(metadata: Dict[str, Any]) -> str:
    """
    Returns list of supported OSes for a specific role

    Args:
        metadata (Dict[str, Any]): role metadata

    Returns:
        str: [description]
    """
    platforms = metadata.get("platforms", [])
    repository = metadata.get("repository", None)

    supported_oses = []
    for platform in platforms:
        name = str(platform.get("name", None)).lower()

        img = "https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/"
        if "arch" in name:
            img += "archlinux.png"
        elif "centos" in name or "el" in name:
            img += "centos.png"
        elif "debian" in name:
            img += "debian.png"
        elif "fedora" in name:
            img += "fedora.png"
        elif "freebsd" in name:
            img += "freebsd.png"
        elif "mac" in name:
            img += "macos.png"
        elif "ubuntu" in name:
            img += "ubuntu.png"
        elif "windows" in name:
            img += "windows.png"
        else:
            raise ValueError(f"Could not find icon for platform {name}")

        if repository:
            supported_oses.append(
                f"<img src=\"{img}\" href=\"{repository}#supported-operating" \
                f"-systems\" target=\"_blank\" />")
        else:
            supported_oses.append(
                f"<img src=\"{img}\" target=\"_blank\" />")

    return "".join(supported_oses)


def get_role_dependency_status(metadata: Dict[str, Any]) -> str:
    """
    Returns role status

    Args:
        metadata (Dict[str, Any]): role metadata

    Returns:
        str: role status
    """
    repository_status = metadata.get("repository_status", None)
    repository = metadata.get("repository", None)
    role_name = metadata.get("role_name", None)
    namespace = metadata.get("namespace", None)

    if not repository_status:
        return "Unavailable"

    img = f"<img src=\"{repository_status}\" />"
    if not repository:
        return img

    return f"<a href=\"{repository}\" title=\"{namespace}.{role_name}'s repos" \
           f"itory\" target=\"_blank\">{img}</a>"
