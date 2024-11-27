"""
Renames files based on their modification date, and moves them to a chosen
destination under the folder structure:
{year_modified}/{photos | videos | documents | recordings}.
"""

import os
from cli_args import exit_if_args_invalid, get_args
from exceptions import DirNotEmptyError, InvalidExtensionError, \
    NoExtensionError
from ext_mappings import get_ext_mappings, update_ext_mappings
from process_file import ProcessFile
from send2trash import send2trash

args = get_args(docstring=__doc__)
exit_if_args_invalid(cli_args=args)

update_ext_mappings(args.origin)
inverted_mappings = get_ext_mappings(inverted=True)

if args.verbose:
    print("\nMoving files...\n")

errors = {
    "copies": {},
    "directory": {},
    "file": {},
}
dirs = set()
for filepath in args.origin.rglob("*"):
    try:
        Process = ProcessFile(
            copyto_dest=args.copyto,
            dest=args.destination,
            exts_to_filetypes=inverted_mappings,
            original_path=filepath,
        )
    except (InvalidExtensionError, NoExtensionError) as ex1:
        if os.path.isdir(filepath):
            dirs.add(filepath)
        else:
            errors["file"][filepath] = str(ex1)
    else:
        try:
            Process.make_dirs()
        except OSError as ex2:
            errors["file"][filepath] = str(ex2)
        else:
            try:
                new_filepath = Process.move()
            except FileNotFoundError as ex3:
                errors["file"][filepath] = str(ex3)
            else:
                if args.verbose:
                    print(f"Moved: {Process.original_path} -> {new_filepath}")
                if Process.copyto_dest is not None:
                    try:
                        Process.copy()
                    except (OSError, ValueError) as ex4:
                        errors["copy"][new_filepath] = str(ex4)
                    else:
                        if args.verbose:
                            print(f"Copied: {new_filepath} -> \
{Process.filepath_for_copy}")

if dirs:
    if args.verbose:
        print("\nTrashing directories...\n")

    for dir_path in dirs:
        try:
            if os.listdir(dir_path):
                raise DirNotEmptyError("Directory not empty.")
            else:
                send2trash(dir_path)
        except OSError as ex5:
            errors["directory"][dir_path] = str(ex5)
        else:
            if args.verbose:
                print(f"{dir_path} trashed.")


for error_type, error_list in errors.items():
    if error_list:
        print(f"\n!!!! ==== {error_type.capitalize()} Errors ==== !!!!\n")
        print("Error processing the following paths:")
        for filepath, exception in error_list.items():
            print(f"{filepath} not processed due to exception: {exception}")
