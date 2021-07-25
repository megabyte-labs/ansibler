from ansibler.args.cmd import get_user_arguments
from ansibler.role_dependencies.dependencies import (
    generate_role_dependency_chart
)
from ansibler.utils.help import display_help


def main() -> None:
    """ Entry point for the script """
    run_ansibler()


def run_ansibler() -> None:
    """ Ansibler """
    # Get CMD args
    args = get_user_arguments()

    # Run generate compatibility charts
    if "generate-compatibility-chart" in args:
        print("Not working yet")
    elif "populate-platforms" in args:
        print("Not working yet")
    elif "role-dependencies" in args:
        generate_role_dependency_chart()
    else:
        display_help()


if __name__ == "__main__":
    main()
