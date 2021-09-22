import os
import pathlib
import re
import json
import asyncio
from json.decoder import JSONDecodeError
from typing import Any, Coroutine, Dict, List, Optional
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
    check_file_exists,
    list_files,
    copy_file,
    check_file_exists,
    create_file_if_not_exists,
    read_gitignore
)


ROLES_PATTERN = r"\[.*\]"


async def generate_role_dependency_chart(
    json_file: Optional[str] = "./ansibler.json",
    template: Optional[str] = None,
    variables: Optional[str] = None
) -> Coroutine[None, None, None]:
    """
    Generates role dependency charts. Uses caches whenever possible.
    """
    # TODO: TESTS
    # Read role paths
    role_paths = parse_default_roles(get_default_roles())
    is_playbook = check_file_exists("./ansible.cfg")

    # Read cache
    cache = read_roles_metadata_from_cache()

    # Generate cache if necessary
    if cache is None:
        cache = cache_roles_metadata(role_paths)

    # Task pool
    tasks = []

    paths = [os.path.abspath("./")] if not is_playbook else role_paths
    for role_path in paths:
        if not check_folder_exists(role_path):
            continue

        # Read gitignore
        files_to_ignore = read_gitignore(
            pathlib.Path(role_path) / pathlib.Path(".gitignore"))

        # List ansible dirs
        if is_playbook:
            files = list_files(role_path, "**/meta/main.yml", True)
        else:
            files = list_files(role_path, "meta/main.yml", True)
            role_path = "/".join(role_path.split("/")[:-1])

        for f in files:
            # Skip if in gitignore
            if pathlib.Path(f[0]) in files_to_ignore:
                continue

            # Make sure we're dealing with an ansible project (role or playbook)
            if not is_ansible_dir(f[0].replace("meta/main.yml", "")):
                continue

            # Get the role name
            req_file = f[0].replace("meta/main.yml", "requirements.yml")
            if is_playbook:
                role_name = get_role_name_from_req_file(role_path, req_file)
            else:
                role_name = role_path.split("/")[-1]

            # Append task to the pool
            tasks.append(
                asyncio.ensure_future(
                    generate_single_role_dependency_chart(
                        role_name,
                        req_file,
                        role_path,
                        cache,
                        os.path.basename(json_file),
                        role_paths,
                        template=template,
                        variables=variables
                    )
                )
            )

    # Execute tasks
    await asyncio.gather(*tasks)
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
        raise CommandNotFound("Could not run", " ".join(bash_cmd))

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
        check_folder_exists(directory + "molecule/")
    ))


async def generate_single_role_dependency_chart(
    role_name: str,
    requirement_file: str,
    role_base_path: str,
    cache: Dict[str, Any],
    json_file: Optional[str] = "ansibler.json",
    role_paths: Optional[str] = [],
    template: Optional[str] = None,
    variables: Optional[str] = None
) -> Coroutine[None, None, None]:
    # TODO: TESTS
    try:
        json_basename = os.path.basename(json_file)
        await role_dependency_chart(
            requirement_file,
            role_base_path,
            cache,
            json_file=json_basename,
            role_paths=role_paths,
            template=template,
            variables=variables
        )
    except (ValueError, MetaYMLError) as e:
        print(
            f"\tCouldnt generate dependency chart for {role_name}: {e}")


async def role_dependency_chart(
    requirement_file: str,
    role_base_path: str,
    cache: Dict[str, Any],
    json_file: Optional[str] = "ansibler.json",
    role_paths: Optional[str] = [],
    template: Optional[str] = None,
    variables: Optional[str] = None
) -> Coroutine[None, None, None]:
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
            if role_paths:
                print(f"\tDoing full re-scan...")
                new_cache = cache_roles_metadata(role_paths, cache)
                return await role_dependency_chart(
                    requirement_file,
                    role_base_path,
                    new_cache,
                    json_file=json_file
                )

            print(f"\tReading dependency {dep} from ansible-galaxy")
            dependency_metadata = get_from_ansible_galaxy(dep)
            append_role_to_cache(dep_name, dependency_metadata, cache)

        role_dependencies.append(
            get_dependency_metadata(
                dependency_metadata,
                role_base_path \
                    if role_base_path.endswith("/") \
                    else role_base_path + "/" + role_name,
                template,
                variables
            )
        )

    if role_base_path.startswith("./"):
        role_path = "/" + role_base_path + "/" + role_name + "/"
    else:
        role_path = role_base_path + "/" + role_name + "/"

    data = {}
    ansibler_json_file = role_path + json_file

    if not check_file_exists(ansibler_json_file):
        create_file_if_not_exists(ansibler_json_file)

    try:
        with open(ansibler_json_file) as f:
            data = json.load(f)

        if isinstance(data, list):
            raise JSONDecodeError()
    except (JSONDecodeError, FileNotFoundError):
        data = {}

    data["role_dependencies"] = role_dependencies

    copy_file(ansibler_json_file, ansibler_json_file, json.dumps(data), True)
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


def get_dependency_metadata(
    dependency_metadata: Dict[str, Any],
    role_base_path: str,
    template: Optional[str] = None,
    variables: Optional[str] = None
) -> List[str]:
    """
    Returns formatted dependency's metadata

    Args:
        dependency_metadata (Dict[str, Any]): metadata
        role_base_path (str): role path
        template (str): repo status template
        variables (Dict[str, str]): role variables

    Returns:
        List[str]: formatted metadata
    """
    # TODO: TESTS
    supported = get_role_dependency_supported_oses(dependency_metadata)
    if supported:
        supported = f"<div align=\"center\">{supported}</div>"

    if template:
        status = get_role_dependency_status_from_template(template, variables)
    else:
        status = get_role_dependency_status(dependency_metadata, role_base_path)

    if status:
        status = f"<div align=\"center\">{status}</div>"

    return [
        get_role_dependency_link(dependency_metadata),
        get_role_dependency_description(dependency_metadata),
        supported,
        status
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
        alt = ""
        if "arch" in name:
            img += "archlinux.png"
            alt = "Arch"
        elif "centos" in name or "el" in name:
            img += "centos.png"
            alt = "EL"
        elif "debian" in name:
            img += "debian.png"
            alt = "Debian"
        elif "fedora" in name:
            img += "fedora.png"
            alt = "Fedora"
        elif "freebsd" in name:
            img += "freebsd.png"
            alt = "FreeBSD"
        elif "mac" in name:
            img += "macos.png"
            alt = "MacOS"
        elif "ubuntu" in name:
            img += "ubuntu.png"
            alt = "Ubuntu"
        elif "windows" in name:
            img += "windows.png"
            alt = "Windows"
        elif "generic" in name:
            img += "linux.png"
            alt = "GenericUNIX"
        else:
            raise ValueError(f"Could not find icon for platform {name}")

        if repository:
            supported_oses.append(
                f"<img src=\"{img}\" href=\"{repository}#supported-operating" \
                f"-systems\" alt=\"{alt}\" />")
        else:
            supported_oses.append(
                f"<img src=\"{img}\" alt=\"{alt}\" />")

    supported_oses = "".join(supported_oses)
    return supported_oses if supported_oses else "❔"


def get_role_dependency_status(metadata: Dict[str, Any], role_path: str) -> str:
    """
    Returns role status

    Args:
        metadata (Dict[str, Any]): role metadata
        role_path (str): role path

    Returns:
        str: role status
    """
    # Looks for .variables.json
    role_name = metadata.get("role_name", None)
    if not role_path.endswith("/"):
        variables_json = role_path + "/" + "variables.json"
    else:
        variables_json = role_path + "variables.json"

    # Return question mark if it the file does not exist
    if not role_name or not check_file_exists(variables_json):
        return "❔"

    # Read variables json file
    data = {}
    try:
        with open(variables_json) as f:
            data = json.load(f)
    except:
        pass

    status = data.get("role_dependencies_status_format", None)
    if status is None:
        return "❔"

    # Replace {{ role_name }} ocurrences
    status = status.replace(r"{{ role_name }}", role_name)
    return status


def get_role_dependency_status_from_template(
    template: str, variables: Dict[str, str]
) -> str:
    """
    Returns role status from template

    Args:
        template (str): repo status template
        variables (Dict[str, str]): role variables

    Returns:
        str: role status
    """
    new_template = template[:]

    for variable, value in variables.items():
        new_template = new_template.replace("{{ " + variable + " }}", value)
        new_template = new_template.replace("{{" + variable + "}}", value)

    return new_template
