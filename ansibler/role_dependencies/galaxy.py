import json
from typing import Any, Dict, Tuple
import requests
from ansibler.utils.subprocesses import get_subprocess_output
from ansibler.exceptions.ansibler import RoleMetadataError


GALAXY_BASE = """
https://galaxy.ansible.com/api/internal/ui/repo-or-collection-detail/
"""


def get_from_ansible_galaxy(role: str) -> Dict[str, Any]:
    """
    Gets role metadata from ansible-galaxy by making a GET request to
    galaxy.ansible.com/api/internal/ui/repo-or-collection-detail

    Args:
        role (str): role in the form {{role_namespace}}.{{role_name}}

    Raises:
        RoleMetadataError: raised when role not found

    Returns:
        Dict[str, Any]: role metadata
    """
    role_namespace, role_name = get_namespace_and_name_from_role(role)
    galaxy_url = build_ansible_galaxy_url(role_namespace, role_name)

    # Make request
    response = requests.get(galaxy_url)

    # Get description from ansible galaxy response
    description = get_role_description_from_galaxy_response(response)

    if not description:
        print(f"Role {role} not found in galaxy.")
        description = "Description unavailable"

    return {
        "namespace": role_namespace,
        "role_name": role_name,
        "description": description
    }


def get_namespace_and_name_from_role(role: str) -> Tuple[str, str]:
    """
    Extract namespace and name for a role.

    Args:
        role (str): role in the form {{role_namespace}}.{{role_name}}

    Returns:
        Tuple[str, str]: namespace, name
    """
    # role comes in the form {{role_namespace}}.{{role_name}}, so split by .
    role_data = role.split(".")
    role_namespace, role_name = role_data[0], role_data[1]
    return role_namespace, role_name


def build_ansible_galaxy_url(role_namespace: str, role_name: str) -> str:
    """
    Build ansible galaxy URL from the given role.

    Args:
        role_namespace (str): role namespace
        role_name (str): role name

    Returns:
        str: url
    """
    # TODO: tests
    return f"{GALAXY_BASE}" \
           f"?namespace={role_namespace}" \
           f"&name={role_name}" \
           f"&format=json"


def get_role_description_from_galaxy_response(
    response: requests.Response
) -> str:
    """
    Extract description for a role from galaxy response

    Args:
        response (requests.Response): response from ansible galaxy (json body) 

    Returns:
        str: description
    """
    # Parse json response
    try:
        data = json.loads(response.text)
    except:
        data = {}

    # description is in .data.repository.description
    return data.get("data", {}) \
        .get("repository", {}) \
        .get("description", None)
