import re
from typing import Any, Dict, List, Optional, Tuple
from ansibler.exceptions.ansibler import MoleculeTestParseError


CONVERGE_START_PATTERN = "PLAY \[Converge\]"
PLAY_RECAP_PATTERN = "PLAY RECAP"

IDEMPOTENCE_START_PATTERN = r"INFO(\s)+Running(.*)idempotence"
PLAY_FINISH_PATTERN = r"INFO(\s)+(.*)"
PLAY_NAME_PATTERN = r"INFO\s+Running.*>\s*(\w.*)"

PLAY_RECAP_OS_NAME_PATTERN = r"^\s?[^\s]*"
PLAY_RECAP_PARALLEL_OS_ID_PATTERN = \
    r"-[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-" \
    r"[A-Za-z0-9]{12}"

OK_COUNT_PATTERN = r"ok=(\d*)"
CHANGED_COUNT_PATTERN = r"changed=(\d*)"
UNREACHABLE_COUNT_PATTERN = r"unreachable=(\d*)"
FAILED_COUNT_PATTERN = r"failed=(\d*)"
SKIPPED_COUNT_PATTERN = r"skipped=(\d*)"
RESCUED_COUNT_PATTERN = r"rescued=(\d*)"
IGNORED_COUNT_PATTERN = r"ignored=(\d*)"


def parse_test(test: str) -> Dict[str, Any]:
    """[summary]

    Args:
        test (str): molecule test content

    Returns:
        Dict[str, Any]: [description]
    """
    parsed_test = {}

    # Scan text in test for first ocurrence of PLAY [Converge]
    # (This is where the role first starts installing the first time around)
    converge_index = scan_molecule_results(
        test, scan_for=CONVERGE_START_PATTERN, start_from=0)

    # (This is where the role first starts installing the first time around)
    converge_recap_start = scan_molecule_results(
        test, scan_for=PLAY_RECAP_PATTERN, start_from=converge_index)

    converge_recap_end = scan_molecule_results(
        test, scan_for="\n\n", start_from=converge_recap_start)

    # Extract section
    parsed_test["converge"] = {
        "play_recap": parse_play_recap(
            test[converge_recap_start:converge_recap_end]
        )
    }

    # For idempotency column, continue in text until you see PLAY [Converge]
    idempotency_index = scan_molecule_results(
        test, scan_for=CONVERGE_START_PATTERN, start_from=converge_recap_end
    )

    # If only one [Converge] section, dont calculate the idempotency indicator
    if not idempotency_index:
        parsed_test["idempotence"] = {}
        return parsed_test

    # If another [Converge] section was found...
    # Go to next occurrence of PLAY RECAP
    idempotency_recap_start = scan_molecule_results(
        test, scan_for=PLAY_RECAP_PATTERN, start_from=idempotency_index)

    idempotency_recap_end = scan_molecule_results(
        test, scan_for="\n\n", start_from=idempotency_recap_start)

    # Extract section
    parsed_test["idempotence"] = {
        "play_recap": parse_play_recap(
            test[idempotency_recap_start:idempotency_recap_end]
        )
    }

    # Scan through the results and mark anything that has any changed
    return parsed_test


def scan_molecule_results(
    results: str,
    scan_for: str,
    start_from: Optional[int] = 0
) -> int:
    # Slice molecule results text
    results_substr = results[start_from:]

    # Search for pattern
    m = re.search(scan_for, results_substr)
    if m:
        return m.start() + start_from

    return None


def parse_play_name(play_dump: str) -> str:
    """
    Extracts the name of the PLAY from the dump.

    Args:
        play_dump (str): molecule test dump

    Raises:
        MoleculeTestParseError: raised when the play name wasn't found

    Returns:
        str: play name
    """
    m = re.search(PLAY_NAME_PATTERN, play_dump)
    if not m:
        raise MoleculeTestParseError("No PLAY NAME found")

    return m.group(1)


def parse_play_recap(play_dump: str) -> List[Dict[str, Any]]:
    """
    Parses PLAY RECAP

    Args:
        play_dump (str): molecule test dump (play section)

    Returns:
        List[Dict[str, Any]]: list of recaps per OS
    """
    recap = []
    recap_lines = play_dump.splitlines()

    # Iterate lines, but skip first (PLAY RECAP ***)
    for recap_line in recap_lines[1:]:
        os_name, os_version = parse_os(recap_line)
        if not os_name:
            continue

        recap.append({
            "os_name": os_name,
            "os_version": os_version,
            "ok": parse_recap_value(
                OK_COUNT_PATTERN, recap_line),
            "changed": parse_recap_value(
                CHANGED_COUNT_PATTERN, recap_line),
            "unreachable": parse_recap_value(
                UNREACHABLE_COUNT_PATTERN, recap_line),
            "failed": parse_recap_value(
                FAILED_COUNT_PATTERN, recap_line),
            "skipped": parse_recap_value(
                SKIPPED_COUNT_PATTERN, recap_line),
            "rescued": parse_recap_value(
                RESCUED_COUNT_PATTERN, recap_line),
            "ignored": parse_recap_value(
                IGNORED_COUNT_PATTERN, recap_line)
        })

    return recap


def parse_os(recap: str) -> Tuple[str, str]:
    """
    Parses OS name and version from a PLAY RECAP line

    Args:
        recap (str): play recap line

    Returns:
        Tuple[str, str]: os name, version
    """
    m = re.search(PLAY_RECAP_OS_NAME_PATTERN, recap)
    if not m:
        return None, None

    # Replace molecule parallel ID
    os = m.group()
    os = re.sub(PLAY_RECAP_PARALLEL_OS_ID_PATTERN, "", os)

    # Split to get name, version
    os_data = os.split("-")

    if len(os_data) > 1:
        os_name = os_data[0]

        version = None
        version_index = None

        os_vers = os_data[1:]
        for i, v in enumerate(os_vers):
            if v.replace(".", "").isnumeric():
                version = v
                version_index = i
                break

        if version is None:
            version_index = 0
            version = os_vers[0]

        codename = version if len(os_vers) <= 1 else f"{version} ("
        remaining_text = []
        for i, c in enumerate(os_vers):
            if i != version_index:
                remaining_text.append(c)

        if len(remaining_text) >= 1:
            if "centos" in os_name.lower():
                os_name += f" {' '.join(remaining_text).title()}"
                codename = codename.rstrip(" (")
            else:
                codename += f"{' '.join(remaining_text).title()})"

        return os_name, codename

    return os_data[0], None


def parse_recap_value(pattern: str, recap: str) -> int:
    """
    Parses a PLAY RECAP value (ok count, failed count, etc..)

    Args:
        pattern (str): pattern to use
        recap (str): play recap line

    Returns:
        int: parsed value
    """
    m = re.search(pattern, recap)
    if not m:
        return -1
    return int(m.group(1))
