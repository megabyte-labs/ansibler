from unittest import TestCase
from unittest.mock import patch
from ansibler.role_dependencies.dependencies import (
    get_default_roles,
    parse_default_roles,
    get_role_dependency_link,
    get_role_dependency_description,
    get_role_dependency_supported_oses,
    get_role_dependency_status
)
from ansibler.exceptions.ansibler import CommandNotFound, RolesParseError


class TestRoleDependencies(TestCase):
    VALID_DEFAULT_ROLES = "DEFAULT_ROLES_PATH(/opt/Playbooks/ansible.cfg) = [" \
        "'/opt/Playbooks/roles/applications', '/opt/Playbooks/roles/crypto', " \
        "'/opt/Playbooks/roles/helpers', '/opt/Playbooks/roles/languages', '/" \
        "opt/Playbooks/roles/misc', '/opt/Playbooks/roles/services', '/opt/Pl" \
        "aybooks/roles/system', '/opt/Playbooks/roles/tools', '/opt/Playbooks" \
        "/roles/virtualization', '/root/.ansible/roles', '/usr/share/ansible/" \
        "roles', '/etc/ansible/roles']"

    @patch("ansibler.role_dependencies.dependencies.get_subprocess_output")
    def test_get_roles(self, mock_get_subprocess_output):
        """
        Test get roles

        Args:
            mock_get_subprocess_output (Mock): get_subprocess_output mock
        """
        mock_get_subprocess_output.return_value = "DEFAULT_ROLES_PATH (ansible)"
        roles = get_default_roles()
        self.assertEqual(roles, "DEFAULT_ROLES_PATH (ansible)")

    @patch("ansibler.role_dependencies.dependencies.get_subprocess_output")
    def test_get_roles_ansible_not_installed(self, mock_get_subprocess_output):
        """
        Makes sure an exception is raised when Ansible is not installed.

        Args:
            mock_get_subprocess_output (Mock): get_subprocess_output mock
        """
        mock_get_subprocess_output.return_value = "command not found"
        with self.assertRaises(CommandNotFound):
            _ = get_default_roles()

    def test_parse_default_roles(self):
        """
        Test parse default roles
        """
        roles = parse_default_roles(self.VALID_DEFAULT_ROLES)
        self.assertEqual(len(roles), 12)

    def test_parse_invalid_default_roles(self):
        """
        Makes sure an exception is raised when roles is improperly formatted
        """
        with self.assertRaises(RolesParseError):
            _ = parse_default_roles("invalid roles")

    def test_get_role_dependency_link(self):
        """
        Test get role dependency link
        """
        l = get_role_dependency_link({"role_name": "role", "namespace": "user"})

        expected = \
            f"<a href=\"https://galaxy.ansible.com/user/role\"" \
            f"title=\"user.role on Ansible Galaxy\" target=\"_" \
            f"blank\">user.role</a>"

        self.assertEqual(l, expected)

    def test_get_role_dependency_description(self):
        """
        Test get role dependency description
        """
        d = get_role_dependency_description({"description": "foo"})
        self.assertEqual(d, "foo")

    def test_get_role_dependency_supported_oses(self):
        """
        Test get role dependency supported OSs
        """
        metadata = {
            "platforms": [{"name": "Ubuntu"}, {"name": "MacOSX"}],
            "repository": "repo"
        }
        r = get_role_dependency_supported_oses(metadata)
        self.assertIn(
            "gitlab.com/megabyte-labs/assets/-/raw/master/icon/ubuntu.png", r)

    def test_get_role_dependency_supported_oses_invalid_os(self):
        """
        Makes sure get role dependency supported oses raises an exception when
        an invalid platform is read
        """
        metadata = {
            "platforms": [{"name": "InvalidOS"}],
            "repository": "repo"
        }
        with self.assertRaises(ValueError):
            _ = get_role_dependency_supported_oses(metadata)

    def test_get_role_dependency_status(self):
        """
        Test get role dependency status
        """
        metadata = {
            "role_name": "role",
            "namespace": "user",
            "repository": "foo",
            "repository_status": "bar"
        }
        r = get_role_dependency_status(metadata)

        expected = "<a href=\"foo\" title=\"user.role's repository\" target=" \
                   "\"_blank\"><img src=\"bar\" /></a>"

        self.assertEqual(r, expected)

    def test_get_role_dependency_status_unavaiable_repo(self):
        """
        Test get role dependency status when repo is unavailable (null)
        """
        metadata = {"repository_status": "foo"}
        r = get_role_dependency_status(metadata)
        self.assertEqual(r, "<img src=\"foo\" />")

    def test_get_role_dependency_status_unavailable_status(self):
        """
        Test get role dependency status when repo status is unavailable (null)
        """
        r = get_role_dependency_status({"repository_status": None})
        self.assertEqual(r, "Unavailable")
