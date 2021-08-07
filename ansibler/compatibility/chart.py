from datetime import datetime
import re
import json
from typing import Any, Dict, List, Optional, Tuple
from ansibler.utils.files import (
    check_file_exists, check_folder_exists, list_files, copy_file
)
from ansibler.exceptions.ansibler import (
    MoleculeTestParseError, MoleculeTestsNotFound, NoPackageJsonError
)
from ansibler.molecule_test.parse import parse_test


MOLECULE_RESULTS_DIR = "./molecule-results/"
FILTER_FILES_PATTERN = r"\d{4}-\d{2}-\d{2}-.*.txt"


def generate_compatibility_chart(
    molecule_results_dir: Optional[str] = None,
    inline_replace: Optional[bool] = False
) -> None:
    if molecule_results_dir is None:
        molecule_results_dir = MOLECULE_RESULTS_DIR

    # TODO: TESTS
    # Check molecule-results dir and ./package.json exist
    if not check_folder_exists(molecule_results_dir):
        raise MoleculeTestsNotFound("Couldn't find molecule results dir")

    if not check_file_exists("./package.json"):
        raise NoPackageJsonError("Couldn't find package.json in this dir")

    # Get list of molecule test files
    test_files = list_files(molecule_results_dir, absolute_path=True)
    test_files = [
        (file_name, file_date)
        for file_name, file_date in test_files
        if re.search(FILTER_FILES_PATTERN, file_name)
    ]

    # Prepare to build blueprint.compatibility array
    compat = [["OS Family", "OS Version", "Status", "Idempotent", "Tested On"]]
    temp_compat = {}

    # Parse test files
    for test_file, test_date in test_files:
        try:
            converge, idempotence = read_molecule_tests(test_file)

            # Skip if converge is invalid
            if not converge:
                continue

            # Read play recaps and add them to temp_compat if they are the most
            # recent for a given OS
            play_recap = converge.get("play_recap", [])
            for recap in play_recap:
                os, recap_summary = get_play_recap_summary(
                    recap, idempotence, test_date)

                if os in temp_compat and test_date < temp_compat[os]["added"]:
                    continue

                temp_compat[os] = recap_summary
        except MoleculeTestParseError as e:
            print(f"Error while parsing molecule test file {test_file}: {e}")

    # Add to blueprint.compatibility
    add_items_to_blueprint_compatibility(temp_compat, compat)

    # Populate package.json
    data = {}
    with open("./package.json") as f:
        data = json.load(f)

    blueprint = data.get("blueprint", {})
    blueprint["compatibility"] = compat

    data["blueprint"] = blueprint

    out = "./package.json" if inline_replace else "./package.ansibler.json"

    # Save
    copy_file("./package.json", out, json.dumps(data), True)
    print("Done")


def read_molecule_tests(
    test_file: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Reads converge and idempotence tests from a test file.

    Args:
        test_file (str): test file path

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: converge and idempotence tests
    """
    # TODO: TESTS
    molecule_test_dump = ""

    with open(test_file) as f:
        molecule_test_dump = f.read()

    test = parse_test(molecule_test_dump)
    converge = test.get("converge", {})
    idempotence = test.get("idempotence", {})

    return converge, idempotence


def get_play_recap_summary(
    recap: Dict[str, Any], idempotence: Dict[str, Any], test_date: datetime
) -> Tuple[str, Dict[str, Any]]:
    """
    Returns a summary of a converge play recap.

    Args:
        recap (Dict[str, Any]): play recap
        idempotence (Dict[str, Any]): corresponding idempotence test

    Returns:
        Tuple[str, Dict[str, Any]]: os, play recap summary
    """
    # TODO: TESTS
    os_name = recap.get("os_name")
    os_version = recap.get("os_version")
    success = did_play_succeed(recap)
    idempotent = is_idempotent(recap, idempotence)

    os = f"{os_name}-{os_version}"

    return os, {
        "os_family": os_name,
        "os_version": os_version,
        "success": success,
        "idempotent": idempotent,
        "added": test_date
    }


def did_play_succeed(
    recap: Dict[str, Any],
    idempotency_play: Optional[bool] = False
) -> bool:
    """
    Checks if a play succeeded.

    Args:
        recap (Dict[str, Any]): play recap
        idempotency_play (bool, optional): idempotence play? Defaults to False.

    Returns:
        bool: whether successful or not
    """
    # TODO: TESTS
    ok = recap.get("ok", 0)
    failed = recap.get("failed", 0)
    unreachable = recap.get("unreachable", 0)

    if idempotency_play:
        changed = recap.get("changed", 0)
        return ok > 0 and not failed and not unreachable and not changed

    return ok > 0 and failed == 0 and unreachable == 0


def is_idempotent(
    recap: Dict[str, Any], idempotence_test: Dict[str, Any]
) -> bool:
    """
    Checks if a test was idempotent.

    Args:
        recap (Dict[str, Any]): play recap
        idempotence_test (Dict[str, Any]): corresponding idempotence test

    Returns:
        bool: whether idempotent or not
    """
    # TODO: TESTS
    idempotence_results = idempotence_test.get("play_recap", [])

    if not idempotence_results:
        return None

    recap_os_name =  recap.get("os_name")
    recap_os_version = recap.get("os_version")

    for result in idempotence_results:
        idp_os_name = result.get("os_name")
        idp_os_version = result.get("os_version")

        if idp_os_name == recap_os_name and idp_os_version == recap_os_version:
            return did_play_succeed(result, idempotency_play=True)

    return None


def add_items_to_blueprint_compatibility(
    items: List[Dict[str, Any]], compat: List[List[str]]
) -> None:
    """
    Appends items to the final blueprint compatibility array.

    Args:
        items (List[Dict[str, Any]]): items to add
        compat (List[List[str]]): List to append the items to.
    """
    # TODO: TESTS
    for _, data in items.items():
        idempotent = data.get("idempotent", None)
        if idempotent == True:
            idempotent = "✅"
        else:
            idempotent = "❌"

        compat.append([
            data["os_family"],
            data["os_version"],
            "✅" if data["success"] else "❌",
            idempotent,
            custom_strftime("%B {S}, %Y", data["added"])
        ])


def custom_strftime(format: str, t: datetime) -> str:
    """
    Custom time format containing English day suffixes (st, nd, rd, th).

    Args:
        format (str): format
        t (datetime): datetime

    Returns:
        (str): formatted datetime
    """
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def suffix(d: int) -> str:
    """
    Retuns DAY NUMBER date suffix.

    Args:
        d (int): day

    Returns:
        str: suffix
    """
    # TODO: TESTS
    if 11 <= d <= 13:
        return "th"
    else:
        return { 1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
