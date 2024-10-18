"""
Renames files based on their modification date, and moves them to a chosen
destination under the folder structure:
{year_modified}/{photos | videos | documents | recordings}.
"""

import argparse
import functions
import os
from dotenv import load_dotenv
from file_to_process import FileToProcess
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

paths_to_trash = set()
for filepath in args.origin.rglob("*"):
    if os.path.isdir(filepath):
        paths_to_trash.add(filepath)
        continue

    ftp = FileToProcess(
        dest=args.destination,
        exts_to_filetypes=reversed_mappings,
        og_path=filepath
    )

    ftp.create_dirs()
    new_filepath = ftp.move()

    if args.verbose:
        print(f"{ftp.og_path} -> {new_filepath}")

if args.verbose and paths_to_trash:
    print("\nTrashing folders...\n")

for path_to_trash in paths_to_trash:
    if os.path.isdir(path_to_trash) and not os.listdir(path_to_trash):
        send2trash(path_to_trash)

        if args.verbose:
            print(f"{path_to_trash} trashed.")
