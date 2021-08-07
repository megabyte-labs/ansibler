from argparse import ArgumentParser, ArgumentError
from typing import Dict
from ansibler import name, __version__

ARGS = [
    {
        "arg_name": "generate-compatibility-chart",
        "arg_help": "Generates compatibilty chart",
        "arg_action": "store_true"
    },
    {
        "arg_name": "populate-platforms",
        "arg_help": "Populate platforms",
        "arg_action": "store_true",
    },
    {
        "arg_name": "role-dependencies",
        "arg_help": "Role dependencies",
        "arg_action": "store_true"
    },
    {
        "arg_name": "molecule-results-dir",
        "arg_help": "Molecule results directory " \
                    "(works for --generate-compatibility-chart only)"
    },
    {
        "arg_name": "inline-replace",
        "arg_help": "Overwrite files with the ansibler generated output",
        "arg_action": "store_true"
    },
    {
        "arg_name": "clear-cache",
        "arg_help": "Clears ansibler cache",
        "arg_action": "store_true"
    },
    { "arg_name": "version", "arg_help": "project version" },
]


def get_user_arguments() -> Dict[str, str]:
    """
    Configures argument parser, then gets the ones entered by the user

    Returns:
        Dict[str, str]: user arguments ({ name: value, ... })
    """
    parser = configure_parser()
    user_args = read_parser_args(parser)
    return user_args


def configure_parser() -> ArgumentParser:
    """
    Instantiates the argument parser instance and adds the accepted arguments

    Returns:
        argparse.ArgumentParser: parser
    """
    parser = ArgumentParser(allow_abbrev=False)

    for arg in ARGS:
        validate_arg(arg)

        if arg.get("arg_name", None) == "version":
            parser.add_argument(
                "-v",
                f"--{arg.get('arg_name')}",
                action="version",
                version=f"{name} {__version__}",
                help=arg.get("arg_help")
            )
        elif arg.get("arg_action", None) != None:
            parser.add_argument(
                f"--{arg.get('arg_name')}",
                action=arg.get("arg_action"),
                help=arg.get("arg_help")
            )
        else:
            parser.add_argument(
                f"--{arg.get('arg_name')}",
                help=arg.get("arg_help")
            )

    return parser


def validate_arg(arg: Dict[str, str]) -> None:
    """
    Validates argument

    Args:
        arg (Dict[str, str]): argument to check

    Raises:
        ValueError: invalid argument
    """
    if not arg.get("arg_name", None) or not arg.get("arg_help", None):
        raise ValueError("Invalid argument")


def read_parser_args(parser) -> Dict[str, str]:
    """
    Reads arguments entered by the user

    Args:
        parser (argparse.ArgumentParser): parser

    Returns:
        Dict[str, str]: user arguments ({ name: value, ... })
    """
    args = parser.parse_args()
    user_args = {}

    for arg in ARGS:
        # python's argparse changes dashes (-) to underscores (_) internally
        arg_name = arg.get("arg_name")
        formatted_arg_name = arg_name.replace("-", "_")

        # Get parsed argument
        parsed_arg_val = getattr(args, formatted_arg_name, None)
        if parsed_arg_val:
            user_args[arg_name] = parsed_arg_val

    # If --version is in arguments, make sure it's the only one
    if "version" in user_args.keys() and len(user_args) > 1:
        raise ArgumentError("Invalid option: \"version\"")

    return user_args
