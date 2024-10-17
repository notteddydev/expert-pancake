import json
import os

from pathlib import Path
from settings import EXT_MAPPINGS_FILE
from typing import List


def get_ext_mappings() -> dict:
    """
    Retrieves the filetypes -> extensions mappings from the extensions.json
    file and returns them as a dictionary.
    """
    with open(EXT_MAPPINGS_FILE, "r") as file:
        ext_mappings = json.load(file)

    return ext_mappings


def request_filetype_for_ext(ext: str, filetypes: List) -> str:
    """
    Asks the user to choose which filetype the extension belongs to, and
    returns the chosen filetype.
    """
    choices = "\n".join([f"{i}: {type}" for i, type in enumerate(filetypes)])
    chosen_index = int(input(f"""Please specify to which type the ext, '{ext}'\
, belongs by typing in the corresponding number.\n\n{choices}\n"""))
    valid_choice = 0 <= chosen_index < len(filetypes)

    if valid_choice:
        filetype = filetypes[chosen_index]
        correct_question = f"\nExtension: '{ext}' will identify with: \
            '{filetype}'. Is that correct? Y/N\n"
        correct = str(input(correct_question)).lower() == "y"

        if correct:
            return filetype

    print("\nPlease choose again.\n")
    return request_filetype_for_ext(ext, filetypes)


def update_ext_mappings(origin: Path) -> None:
    """
    Goes through the origin directory, and for any extensions that occur
    which are not accounted for in extensions.json, the user is asked to
    provide a filetype. The extensions are then added to the list for that
    filetype in extensions.json.
    """
    ext_mappings = get_ext_mappings()
    recognised_exts = [
        ext
        for exts in ext_mappings.values()
        for ext in exts
    ]

    initial_len = len(recognised_exts)
    for filepath in origin.rglob("*"):
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if not ext or ext in recognised_exts:
            continue

        filetype = request_filetype_for_ext(ext, ext_mappings.keys())
        ext_mappings[filetype].append(ext)
        recognised_exts.append(ext)

    if len(recognised_exts) == initial_len:
        return

    for _, exts in ext_mappings.items():
        exts.sort()

    with open(EXT_MAPPINGS_FILE, "w") as file:
        json.dump(ext_mappings, file, indent=4)
