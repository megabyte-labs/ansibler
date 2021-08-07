from unittest import TestCase
from unittest.mock import patch
import argparse
from ansibler.args import cmd
from ansibler.args.cmd import configure_parser, validate_arg, read_parser_args


class TestArguments(TestCase):
    VALID_ARGUMENTS = [
        {
            "arg_name": "generate-compatibility-chart",
            "arg_help": "help",
            "arg_action": "store_true"
        },
        {
            "arg_name": "populate-platforms",
            "arg_help": "help",
            "arg_action": "store_true",
        },
        {
            "arg_name": "role-dependencies",
            "arg_help": "help",
            "arg_action": "store_true"
        },
        { "arg_name": "version", "arg_help": "help" },
    ]

    INVALID_ARGUMENTS = [
        { "name": "invalid", "help": "invalid help" }
    ]

    def setUp(self) -> None:
        """
        Test case setup
        """
        self.mock_valid_args = patch.object(
            cmd, 'ARGS', return_value=self.VALID_ARGUMENTS
        )
        with self.mock_valid_args:
            self.parser = configure_parser()

    def test_parser_properly_setup(self):
        """
        Tests initialization of parser
        """
        self.assertIsInstance(self.parser, argparse.ArgumentParser)

    def test_parser_improper_setup(self):
        """
        Tests parser fails to initialize when ARGS is not properly set
        ([{"arg_name": "foo", "arg_help": "bar"}, ...}])
        """
        with patch.object(cmd, "ARGS", self.INVALID_ARGUMENTS):
            with self.assertRaises(ValueError):
                _ = configure_parser()

    def test_valid_argument(self):
        """
        Tests valid argument
        """
        self.assertEqual(validate_arg(self.VALID_ARGUMENTS[0]), None)

    def test_invalid_argument(self):
        """
        Tests invalid argument
        """
        with self.assertRaises(ValueError):
            validate_arg(self.INVALID_ARGUMENTS[0])

    def test_read_parser_args(self):
        """
        Makes sure parameters are read
        """
        params = ["ansibler.py", "--populate-platforms"]
        with self.mock_valid_args:
            with patch.object(argparse._sys, "argv", params):
                self.assertEqual(argparse._sys.argv, params)
