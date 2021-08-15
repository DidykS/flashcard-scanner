# scanner/utils.py
# Utility functions.

import json
from typing import Dict, List


def load_list(filepath: str) -> List[Dict]:
    """Load a list of dictionaries from a JSON's filepath.

    Args:
        filepath (str): JSON's filepath.

    Returns:
        A list with the data loaded.
    """
    with open(filepath) as fp:
        lst = json.load(fp)
        return lst


def save_list(
    lst: List[Dict],
    filepath: str,
    ensure_ascii: bool = False,
    sortkeys: bool = False,
) -> None:
    """Save a list of dictionaries to a specific location.

    Args:
        lst (List[Dict]): A list of dictionaries to save.
        filepath (str): A location to save the list to as a JSON file.
        ensure_ascii (bool, optional): Ensure the output is valid ascii characters. Defaults to False.
        sortkeys (bool, optional): Sort keys in dict alphabetically. Defaults to False.
    """
    with open(filepath, "w") as fp:
        json.dump(
            lst, fp=fp, ensure_ascii=ensure_ascii, indent=2, sort_keys=sortkeys
        )
