def get_role_name(role_path: str, meta_file_path: str) -> str:
    """
    Gets role name from its path and meta file path.

    Args:
        role_path (str): role path
        meta_file_path (str): role meta file path.

    Returns:
        str: role name.
    """
    return meta_file_path \
        .replace("meta/main.yml", "") \
        .replace(role_path, "") \
        .strip("/").split("/")[-1]


def get_role_name_from_req_file(base_path: str, req_file_path: str) -> str:
    """
    Gets role name from its base path and requirements.yml path.

    Args:
        base_path (str): role base path
        req_file_path (str): role requirements.yml file path.

    Returns:
        str: role name.
    """
    return req_file_path \
        .replace("requirements.yml", "") \
        .replace(base_path, "") \
        .strip("/")


def get_role_full_path(role_path: str, role_name: str) -> str:
    """
    Get absolute path for a role.

    Args:
        role_path (str): role base path
        role_name (str): role name

    Returns:
        str: role absolute path
    """
    # Append / if necessary
    if role_path.endswith("/"):
        role_full_path = role_path
    else:
        role_full_path = role_path + "/"

    # Build absolute path and return
    role_full_path += role_name
    return role_full_path
