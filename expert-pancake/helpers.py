import json
import os

from pathlib import Path


def request_filetype_for_ext(ext, filepaths_with_ext, filetypes):
    print(f"Please specify to which type the ext: '{ext}' belongs by typing in the corresponding number. Files for that ext are listed below:")
    print("\n".join(filepaths_with_ext))

    for i, type in enumerate(filetypes):
        print(f"{i}: {type}")
    
    index = int(input("Enter the number corresponding to your choice: "))

    if 0 <= index < len(filetypes):
        filetype = filetypes[index]
        correct = str(input(f"\nYou chose '{filetype}' for ext: '{ext}'. Is that correct? Y/N\n")).lower() == "y"

        if correct:
            print(f"\nExtension type: '{ext}' now identifies with: '{filetype}'\n")
            return filetype
    
    print("\nPlease try again.\n")

    return request_filetype_for_ext(ext, filepaths_with_ext, filetypes)


def get_up_to_date_filetypes_and_their_exts(folder_to_process):
    base_dir = Path(__file__).resolve().parent.parent
    ext_file = os.path.join(base_dir, "extensions.json")

    with open(ext_file, "r") as file:
        filetypes_and_their_exts = json.load(file)

    exts_only = [ext for exts in filetypes_and_their_exts.values() for ext in exts]
    unrecognised_exts = dict()

    for filepath in folder_to_process.rglob("*"):
        if os.path.isdir(filepath):
            continue

        _, filepath_ext = os.path.splitext(filepath)
        filepath_ext = filepath_ext.lower()

        if filepath_ext in exts_only:
            continue

        if filepath_ext not in unrecognised_exts.keys():
            unrecognised_exts[filepath_ext] = []

        unrecognised_exts[filepath_ext].append(str(filepath))

    for ext, filepaths in unrecognised_exts.items():
        filetype = request_filetype_for_ext(ext, filepaths, list(filetypes_and_their_exts))
        filetypes_and_their_exts[filetype].append(ext)

    for _, exts in filetypes_and_their_exts.items():
        exts.sort()

    with open(ext_file, 'w') as file:
        json.dump(filetypes_and_their_exts, file, indent=4)

    return filetypes_and_their_exts