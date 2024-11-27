"""
Renames files based on their modification date, and moves them to a chosen
destination under the folder structure:
{year_modified}/{photos | videos | documents | recordings}.
"""

import argparse
import functions
import os
from dotenv import load_dotenv
from exceptions import DirNotEmptyError, InvalidExtensionError, \
    NoExtensionError
from process_file import ProcessFile
from pathlib import Path
from send2trash import send2trash

load_dotenv()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-d", "--destination",
                    help="The directory to move files to.",
                    required=True,
                    type=Path,
                    )
parser.add_argument("-o", "--origin",
                    default=os.environ.get("FOLDER_TO_PROCESS"),
                    help="The directory to move files from.",
                    type=Path,
                    )
parser.add_argument("-v", "--verbose",
                    action="store_const",
                    const=True,
                    default=False,
                    help="Add this for more chit-chat.",
                    )

args = parser.parse_args()

for args_attr in ["destination", "origin"]:
    if not os.path.isdir(getattr(args, args_attr)):
        print(f"{args_attr.capitalize()} does not exist. Exiting.")
        exit()

if not os.listdir(args.origin):
    print("Origin empty. Exiting.")
    exit()

functions.update_ext_mappings(args.origin)

ext_mappings = functions.get_ext_mappings()
reversed_mappings = {
    ext: file_type
    for file_type, exts in ext_mappings.items()
    for ext in exts
}

if args.verbose:
    print("\nMoving files...\n")

errors = {}
dirs = set()
for filepath in args.origin.rglob("*"):
    try:
        Process = ProcessFile(
            dest=args.destination,
            exts_to_filetypes=reversed_mappings,
            og_path=filepath
        )
    except (InvalidExtensionError, NoExtensionError) as ex1:
        if os.path.isdir(filepath):
            dirs.add(filepath)
        else:
            errors[filepath] = str(ex1)
    else:
        try:
            os.makedirs(Process.full_dest, exist_ok=True)
        except OSError as ex2:
            errors[filepath] = str(ex2)
        else:
            try:
                new_filepath = Process()
            except FileNotFoundError as ex3:
                errors[filepath] = str(ex3)
            else:
                if args.verbose:
                    print(f"{Process.og_path} -> {new_filepath}")

if dirs:
    if args.verbose:
        print("\nTrashing directories...\n")

    for dir_path in dirs:
        try:
            if os.listdir(dir_path):
                raise DirNotEmptyError("Directory not empty.")
            else:
                send2trash(dir_path)
        except OSError as ex4:
            errors[dir_path] = str(ex4)
        else:
            if args.verbose:
                print(f"{dir_path} trashed.")

if errors:
    print("\n!!!! ==== Errors ==== !!!!\n")
    print("Error processing the following paths:")
    for filepath, exception in errors.items():
        print(f"{filepath} not processed due to exception: {exception}")
