import os
import pathlib
import json
import asyncio
from json.decoder import JSONDecodeError
from typing import Any, Coroutine, Dict, List, Optional
from ruamel.yaml import YAML
from ansibler.role_dependencies.role_info import get_role_name_from_req_file
from ansibler.role_dependencies.galaxy import get_from_ansible_galaxy
from ansibler.exceptions.ansibler import MetaYMLError, RolesParseError
from ansibler.role_dependencies.cache import (
    read_roles_metadata_from_cache, cache_roles_metadata, append_role_to_cache
)
from ansibler.utils.files import (
    check_folder_exists,
    check_file_exists,
    create_folder_if_not_exists,
    grep_file,
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
                        json_file=json_file,
                        role_paths=role_paths,
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
    # Check if ANSIBLE_CONFIG is defined in envvars and if so,
    # extract default roles from there
    ansible_config_file = os.getenv("ANSIBLE_CONFIG", None)
    if ansible_config_file is not None:
        matches = grep_file(ansible_config_file, "DEFAULT_ROLES_PATH")
        if matches:
            return matches

    # If no matches yet, check from ~/.ansible.cfg
    home_dir = os.path.expanduser("~")
    matches = grep_file(f"{home_dir}/.ansible.cfg", "roles_path")
    if matches:
        return matches

    # If still matches yet, check from /etc/ansible/ansible.cfg.
    matches = grep_file("/etc/ansible/ansible.cfg", "roles_path")
    if matches:
        return matches

    # Else, return empty string
    return ""


def parse_default_roles(default_roles: str) -> List[str]:
    """
    Parses default roles from an ansible.cfg file

    Args:
        default_roles (str): raw roles dump, straight from cmd output

    Raises:
        RolesParseError: default_roles doesnt have the expected format

    Returns:
        List[str]: list of role paths
    """
    if not default_roles:
        return []

    # Split by =
    config_key_value = default_roles.split("=")
    
    if len(config_key_value) < 2:
        raise RolesParseError(f"Couldn't parse roles from: {default_roles}")

    res = [config_key_value[1].strip()]
    return res


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
        await role_dependency_chart(
            requirement_file,
            role_base_path,
            cache,
            json_file=json_file,
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

        role_dependencies.append(get_dependency_metadata(dependency_metadata))

    if role_base_path.startswith("./"):
        role_path = "/" + role_base_path + "/" + role_name + "/"
    else:
        role_path = role_base_path + "/" + role_name + "/"

    data = {}
    ansibler_json_file = role_path + json_file

    if not check_file_exists(ansibler_json_file):
        create_folder_if_not_exists(
            ansibler_json_file.replace(os.path.basename(ansibler_json_file), "")
        )
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
    return metadata.get("description", "Description unavailable")
