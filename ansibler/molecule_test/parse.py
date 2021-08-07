import re
from typing import Any, Dict, List, Tuple
from ansibler.exceptions.ansibler import MoleculeTestParseError


CONVERGE_START_PATTERN = r"INFO(\s)+Running(.*)converge"
IDEMPOTENCE_START_PATTERN = r"INFO(\s)+Running(.*)idempotence"
PLAY_FINISH_PATTERN = r"INFO(\s)+(.*)"
PLAY_NAME_PATTERN = r"INFO\s+Running.*>\s*(\w.*)"
PLAY_RECAP_PATTERN = r"(PLAY RECAP.+?\s)((.+?\s)*)"

PLAY_RECAP_OS_NAME_PATTERN = r"^\s?[^\s]*"
OK_COUNT_PATTERN = r"ok=(\d*)"
CHANGED_COUNT_PATTERN = r"changed=(\d*)"
UNREACHABLE_COUNT_PATTERN = r"unreachable=(\d*)"
FAILED_COUNT_PATTERN = r"failed=(\d*)"
SKIPPED_COUNT_PATTERN = r"skipped=(\d*)"
RESCUED_COUNT_PATTERN = r"rescued=(\d*)"
IGNORED_COUNT_PATTERN = r"ignored=(\d*)"


def parse_test(molecule_test_dump: str) -> Dict[str, Any]:
    """
    Parses a molecule test - includes 'converge' and 'idempotence'

    Args:
        molecule_test_dump (str): molecule test dump

    Returns:
        Dict[str, Any]: parsed molecule test
    """
    test = {}

    converge_test = parse_play(CONVERGE_START_PATTERN, molecule_test_dump)
    if converge_test:
        test["converge"] = converge_test

    try:
        idempotence_test = parse_play(
            IDEMPOTENCE_START_PATTERN, molecule_test_dump)
    except MoleculeTestParseError:
        idempotence_test = None

    if idempotence_test:
        test["idempotence"] = idempotence_test

    return test


def parse_play(play_pattern: str, molecule_test_dump: str) -> Dict[str, Any]:
    """
    Extracts a PLAY from a molecule test dump

    Args:
        play_pattern (str): play start pattern (regexp)
        molecule_test_dump (str): molecule test dump

    Raises:
        MoleculeTestParseError: raised when PLAY not found

    Returns:
        Dict[str, Any]: formatted play
    """
    play = {}

    m = re.search(play_pattern, molecule_test_dump)
    if not m:
        raise MoleculeTestParseError("PLAY not found")

    # Get start and end index
    play_info_dump = m.group()
    play_start, play_end = m.span()[0], -1

    m = re.search(
        PLAY_FINISH_PATTERN,
        molecule_test_dump[play_start + len(play_info_dump):]
    )
    if m:
        play_end = len(molecule_test_dump[:play_start]) + m.span()[1]

    # Parse play name and play recap info
    play_dump = molecule_test_dump[play_start:play_end]
    play["play_name"] = parse_play_name(play_info_dump)
    play["play_recap"] = parse_play_recap(play_dump)

    return play 


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
    play_recap_dump = parse_play_recap_dump(play_dump)

    recap_lines = play_recap_dump.splitlines()
    for recap_line in recap_lines:
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


def parse_play_recap_dump(play_dump: str) -> str:
    """
    Parses PLAY RECAP dump, without any formatting

    Args:
        play_dump (str): molecule test PLAY dump

    Raises:
        MoleculeTestParseError: raised when PLAY RECAP is not found

    Returns:
        str: play recap dump
    """
    m = re.search(PLAY_RECAP_PATTERN, play_dump)
    if not m:
        raise MoleculeTestParseError("Could not parse PLAY RECAP")
    return m.group(2).strip()


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

    # Split to get name, version
    os_data = m.group().split("-")

    if len(os_data) > 1:
        return os_data[0], os_data[1].strip(":").strip()

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
