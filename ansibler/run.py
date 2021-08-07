import sys
from ansibler.args.cmd import get_user_arguments
from ansibler.compatibility.chart import generate_compatibility_chart
from ansibler.platforms.populate import populate_platforms
from ansibler.role_dependencies.dependencies import (
    generate_role_dependency_chart
)
from ansibler.role_dependencies.cache import clear_cache
from ansibler.utils.help import display_help


def main() -> None:
    """ Entry point for the script """
    run_ansibler()


def run_ansibler() -> None:
    """ Ansibler """
    # Get CMD args
    args = get_user_arguments()

    # Check for clear-cache
    if "clear-cache" in args:
        clear_cache()
        print("Cache cleared")

    inline_replace = args.get("inline-replace", False)

    # Run generate compatibility charts
    if "generate-compatibility-chart" in args:
        molecule_results_dir = args.get("molecule-results-dir")
        generate_compatibility_chart(
            molecule_results_dir, inline_replace=inline_replace)
    elif "populate-platforms" in args:
        populate_platforms(inline_replace=inline_replace)
    elif "role-dependencies" in args:
        generate_role_dependency_chart(inline_replace=inline_replace)
    else:
        display_help()


if __name__ == "__main__":
    main()
