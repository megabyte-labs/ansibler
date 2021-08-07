from unittest import TestCase
from unittest.mock import patch
from ansibler.role_dependencies.galaxy import get_from_ansible_galaxy
from ansibler.exceptions.ansibler import RoleMetadataError


class TestGalaxy(TestCase):
    @patch("ansibler.role_dependencies.galaxy.get_subprocess_output")
    def test_get_from_galaxy(self, mock_get_subprocess_output):
        mock_out = "description: Ensures Snap is installed"
        mock_get_subprocess_output.return_value = mock_out

        role = get_from_ansible_galaxy("professormanhattan.snapd")
        expected = {
            "namespace": "professormanhattan",
            "role_name": "snapd",
            "description": "Ensures Snap is installed",
            "repository": None,
            "repository_status": None
        }

        self.assertDictEqual(role, expected)

    @patch("ansibler.role_dependencies.galaxy.get_subprocess_output")
    def test_get_from_galaxy_role_not_found(self, mock_get_subprocess_output):
        mock_get_subprocess_output.return_value = ""
        with self.assertRaises(RoleMetadataError):
            _ = get_from_ansible_galaxy("professormanhattan.snapd")
