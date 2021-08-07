from unittest import TestCase
from unittest.mock import patch
from ansibler.molecule_test.parse import (
    parse_play_name,
    parse_play_recap,
    parse_play_recap_dump,
    parse_os,
    parse_recap_value,
    OK_COUNT_PATTERN
)


class TestParseMolecule(TestCase):
    def test_parse_play_name(self):
        """
        Test extract play name
        """
        dump = "\n\nINFO     Running docker-snap >  idempotence\n\n"
        res = parse_play_name(dump)
        self.assertEqual(res, "idempotence")

    @patch("ansibler.molecule_test.parse.parse_play_recap_dump")
    def test_parse_play_recap(self, mock_parse_play_recap_dump):
        """
        Test parse play recap

        Args:
            mock_parse_play_recap_dump (Mock): parse play recap dump mock 
        """
        play_recap = "Debian-10: ok=16 changed=0 unreachable=0 failed=0 " \
                     "skipped=4 rescued=0 ignored=0\nUbuntu-20.04: ok=16 " \
                     "changed=0 unreachable=0 failed=0 skipped=4 rescued=0 " \
                     "ignored=0"
        mock_parse_play_recap_dump.return_value = play_recap

        res = parse_play_recap(play_recap)
        expected_recap = {
            "ok": 16,
            "changed": 0,
            "unreachable": 0,
            "failed": 0,
            "skipped": 4,
            "rescued": 0,
            "ignored": 0
        }
        expected_recap = [
            {"os_name": "Debian", "os_version": "10", **expected_recap},
            {"os_name": "Ubuntu", "os_version": "20.04", **expected_recap}
        ]

        self.assertEqual(res, expected_recap)

    def test_parse_play_recap_dump(self):
        """
        Test parse play recap dump
        """
        dump = """
        changed: [Ubuntu-21.04]
        PLAY RECAP ******
        expected result

        INFO     Running docker-snap > idempotence
        """
        res = parse_play_recap_dump(dump)
        self.assertEqual(res, "expected result")

    def test_parse_os(self):
        """
        Test parse os
        """
        name, version = parse_os("Debian-10    : ok=19")
        self.assertEqual(f"{name}-{version}", "Debian-10")

    def test_parse_os_no_version(self):
        """
        Test parse os no version
        """
        name, version = parse_os("macos    : ok=19")
        self.assertEqual(f"{name}-{version}", "macos-None")

    def test_parse_recap_value(self):
        """
        Test parse recap value
        """
        res = parse_recap_value(OK_COUNT_PATTERN, "Debian-10: ok=19")
        self.assertEqual(res, 19)

    def test_parse_recap_value_not_exists(self):
        """
        Assert returns -1 when the pattern doesnt return a match
        """
        res = parse_recap_value(OK_COUNT_PATTERN, "")
        self.assertEqual(res, -1)
