import asyncio
import sys
from ansibler.args.cmd import get_user_arguments
from ansibler.compatibility.chart import generate_compatibility_chart
from ansibler.platforms.populate import populate_platforms, read_json_file
from ansibler.role_dependencies.dependencies import (
    generate_role_dependency_chart
)
from ansibler.role_dependencies.cache import clear_cache
from ansibler.utils.files import check_file_exists
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

    json_file = args.get("json-file", "./ansibler.json")

    # Run generate compatibility charts
    if "generate-compatibility-chart" in args:
        molecule_results_dir = args.get("molecule-results-dir")
        generate_compatibility_chart(
            molecule_results_dir, json_file=json_file)
    elif "populate-platforms" in args:
        populate_platforms(json_file=json_file)
    elif "role-dependencies" in args:
        repository_status_template = args.get(
            "repository-status-template", None)
        variables = args.get("variables", None)

        # Read repo status template
        if repository_status_template is not None:
            template_is_file = check_file_exists(repository_status_template)
            if template_is_file:
                with open(repository_status_template) as f:
                    repository_status_template = f.read()
                    repository_status_template.replace("\n", "")

        # Read variables
        if variables is not None:
            variables_is_file = check_file_exists(variables)
            if not variables_is_file:
                print("Invalid variables file.")
                sys.exit(1)
            else:
                variables = read_json_file(variables)

        asyncio.run(
            generate_role_dependency_chart(
                json_file=json_file,
                template=repository_status_template,
                variables=variables
            )
        )
    else:
        if "clear-cache" not in args:
            display_help()


if __name__ == "__main__":
    main()
