from unittest import TestCase
from ansibler.role_dependencies.role_info import (
    get_role_full_path,
    get_role_name,
    get_role_name_from_req_file,
)


class TestRoleInfo(TestCase):
    def test_get_role_name(self):
        """
        Test get role name
        """
        role = get_role_name(
            "/home/user/projects/Playbooks/roles/system",
            "/home/user/projects/Playbooks/roles/system/snapd/meta/main.yml"
        )
        self.assertEqual(role, "snapd")

    def test_get_role_name_from_requirements_file(self):
        """
        Test get role name from requirements.yml
        """
        role = get_role_name_from_req_file(
            "/home/user/projects/Playbooks/roles/system",
            "/home/user/projects/Playbooks/roles/system/snapd/requirements.yml"
        )
        self.assertEqual(role, "snapd")

    def test_get_role_full_path(self):
        """
        Test get role full path
        """
        role_path = get_role_full_path(
            "/home/user/projects/Playbooks/roles/system", "snapd")
        self.assertEqual(
            role_path, "/home/user/projects/Playbooks/roles/system/snapd")
