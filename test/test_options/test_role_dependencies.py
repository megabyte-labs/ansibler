from unittest import TestCase
from unittest.mock import patch, MagicMock
from ansibler.options.role_dependencies import (
    get_default_roles, parse_default_roles
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

    @patch("ansibler.options.role_dependencies.get_subprocess_output")
    def test_get_roles(self, mock_get_subprocess_output):
        """
        Test get roles

        Args:
            mock_get_subprocess_output (Mock): get_subprocess_output mock
        """
        mock_get_subprocess_output.return_value = "DEFAULT_ROLES_PATH (ansible)"
        roles = get_default_roles()
        self.assertEqual(roles, "DEFAULT_ROLES_PATH (ansible)")

    @patch("ansibler.options.role_dependencies.get_subprocess_output")
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
