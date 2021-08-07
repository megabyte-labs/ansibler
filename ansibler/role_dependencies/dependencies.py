import re
import json
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional
from ruamel.yaml import YAML
from ansibler.utils.subprocesses import get_subprocess_output
from ansibler.role_dependencies.role_info import get_role_name_from_req_file
from ansibler.role_dependencies.galaxy import get_from_ansible_galaxy
from ansibler.exceptions.ansibler import CommandNotFound, MetaYMLError, RolesParseError
from ansibler.role_dependencies.cache import (
    read_roles_metadata_from_cache, cache_roles_metadata, append_role_to_cache
)
from ansibler.utils.files import (
    check_folder_exists,
    create_folder_if_not_exists,
    check_file_exists,
    list_files,
    copy_file,
    check_file_exists,
    create_file_if_not_exists
)


ROLES_PATTERN = r"\[.*\]"


def generate_role_dependency_chart(
    inline_replace: Optional[bool] = False
) -> None:
    """
    Generates role dependency charts. Uses caches whenever possible.
    """
    # TODO: TESTS
    role_paths = parse_default_roles(get_default_roles())
    if not check_file_exists("./ansible.cfg"):
        role_paths.append("./")

    # Read cache
    cache = read_roles_metadata_from_cache()

    # Generate cache if necessary
    if cache is None:
        cache = cache_roles_metadata(role_paths)
    else:
        cache = cache_roles_metadata(role_paths, cache)

    for role_path in role_paths:
        files = list_files(role_path, "**/package.json", True)
        for f in files:
            if not is_ansible_dir(f[0].replace("package.json", "")):
                continue

            req_file = f[0].replace("package.json", "requirements.yml")
            role_name = get_role_name_from_req_file(role_path, req_file)

            try:
                generate_single_role_dependency_chart(
                    req_file, role_path, cache, inline_replace=inline_replace)
            except (ValueError, MetaYMLError) as e:
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


def is_ansible_dir(directory: str) -> bool:
    """
    Checks if dir is an ansible playbook or role.

    Args:
        directory (str): dir to check

    Returns:
        bool: whether an ansible playbook or role
    """
    return any((
        check_file_exists(directory + "meta/main.yml"),
        check_file_exists(directory + "requirements.yml"),
        check_folder_exists(directory + "molecule/")
    ))


def generate_single_role_dependency_chart(
    requirement_file: str,
    role_base_path: str,
    cache: Dict[str, Any],
    inline_replace: Optional[bool] = False
) -> None:
    # TODO: TESTS
    # Get role's name
    role_name = get_role_name_from_req_file(role_base_path, requirement_file)

    print(f"Generating role dependency for {role_name}")

    role_dependencies = []

    # Read dependencies
    dependencies = read_dependencies(requirement_file)
    # If there's at least one dependency, add headers
    if len(dependencies):
        role_dependencies.append([
            "Dependency",
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
        print(f"\tReading dependency {dep}")
        dependency_metadata = cache.get(dep_name, {})

        # if not found locally, try getting from ansible-galaxy
        if not dependency_metadata:
            print(
                f"\tWARNING: Role {dep} not found locally, trying to get it " \
                "from ansible-galaxy..."
            )
            dependency_metadata = get_from_ansible_galaxy(dep)
            append_role_to_cache(dep_name, dependency_metadata, cache)

        role_dependencies.append(
            get_dependency_metadata(dependency_metadata))

    if role_base_path.startswith("./"):
        role_path = "/" + role_base_path + "/" + role_name + "/"
    else:
        role_path = role_base_path + "/" + role_name + "/"

    data = {}
    package_json_file = role_path + "package.json"
    if not inline_replace:
        new_package_json_file = role_path + "package.ansibler.json"
    else:
        new_package_json_file = package_json_file

    if not check_file_exists(package_json_file):
        create_file_if_not_exists(package_json_file)

    try:
        with open(package_json_file) as f:
            data = json.load(f)
    except JSONDecodeError:
        data = {}

    blueprint = data.get("blueprint", {})
    blueprint["role_dependencies"] = role_dependencies
    data["blueprint"] = blueprint

    copy_file(package_json_file, new_package_json_file, json.dumps(data), True)
    print(f"\tGenerated role dependency chart for {role_name}")


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
    try:
        with open(requirements_file_path) as f:
            yaml = YAML()
            data = yaml.load(f)
    except FileNotFoundError:
        return []

    if data is None:
        return []

    return [role["name"] for role in data.get("roles", []) if "name" in role]


def get_dependency_metadata(dependency_metadata: Dict[str, Any]) -> List[str]:
    """
    Returns formatted dependency's metadata

    Args:
        dependency_metadata (Dict[str, Any]): metadata

    Returns:
        List[str]: formatted metadata
    """
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
    
    return f"<b>" \
           f"<a href=\"https://galaxy.ansible.com/{namespace}/{role_name}\" " \
           f"title=\"{namespace}.{role_name} on Ansible Galaxy\" target=\"_" \
           f"blank\">{namespace}.{role_name}</a></b>"


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
        elif "generic" in name:
            img += "linux.png"
        else:
            raise ValueError(f"Could not find icon for platform {name}")

        if repository:
            supported_oses.append(
                f"<img src=\"{img}\" href=\"{repository}#supported-operating" \
                f"-systems\" target=\"_blank\" />")
        else:
            supported_oses.append(
                f"<img src=\"{img}\" target=\"_blank\" />")

    supported_oses = "".join(supported_oses)
    return supported_oses if supported_oses else "❔"


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
        return "❔"

    img = f"<img src=\"{repository_status}\" />"
    if not repository:
        return img

    return f"<a href=\"{repository}\" title=\"{namespace}.{role_name}'s repos" \
           f"itory\" target=\"_blank\">{img}</a>"
