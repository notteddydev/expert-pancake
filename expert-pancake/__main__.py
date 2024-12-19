"""
Renames files based on their modification date, and moves them to a chosen
destination under the folder structure:
{year_modified}/{photos | videos | documents | recordings}.
"""

import os
import re
import time
from cli_args import exit_if_args_invalid, get_args
from exceptions import DirNotEmptyError
from ext_mappings import get_ext_mappings, update_ext_mappings
from helpers import get_modified_dt_obj, get_dest_filename, process_file
from send2trash import send2trash
from shutil import copy2, move
from settings import IGNORE, YMD_PATTERN

args = get_args(docstring=__doc__)
exit_if_args_invalid(cli_args=args)

update_ext_mappings(args.origin)
filetypes_to_exts = get_ext_mappings(inverted=True)

if args.verbose:
    print("\nMoving files...\n")

errors = {
    "copies": {},
    "directory": {},
    "file": {},
}
dirs = set()
for src_filepath in args.origin.rglob("*"):
    original_filename = os.path.basename(src_filepath)
    original_stem, ext = os.path.splitext(original_filename)

    if not ext:
        if os.path.isdir(src_filepath):
            dirs.add(src_filepath)
        else:
            errors["file"][src_filepath] = "No extension found."
        continue

    filetype = filetypes_to_exts[ext.lower()]
    if filetype == IGNORE:
        errors["file"][src_filepath] = "Extension invalid."
        continue

    modified_dt_obj = get_modified_dt_obj(src_filepath)
    ymd_match = re.match(YMD_PATTERN, original_stem)
    if ymd_match:
        year = ymd_match.group("year")
    else:
        year = time.strftime("%Y", modified_dt_obj)
    relative_dir = os.path.join(year, filetype)
    dest_filename = get_dest_filename(filetype=filetype,
                                      original_stem=original_stem,
                                      modified_dt_obj=modified_dt_obj,
                                      ymd_match=ymd_match,
                                      dest=args.destination,
                                      relative_dir=relative_dir,
                                      ext=ext)

    try:
        moved_to = process_file(src_filepath=src_filepath,
                                dest_filename=dest_filename,
                                relative_dir=relative_dir,
                                dest_parent=args.destination,
                                fn=move,
                                verbose="Moved")
    except (OSError, FileNotFoundError) as ex:
        errors["file"][src_filepath] = str(ex)
        continue

    if args.copydestination is not None:
        try:
            copied_to = process_file(src_filepath=moved_to,
                                     dest_filename=dest_filename,
                                     relative_dir=relative_dir,
                                     dest_parent=args.copydestination,
                                     fn=copy2,
                                     verbose="Copied")
        except OSError as ex:
            errors["copy"][moved_to] = str(ex)
            continue

if dirs:
    if args.verbose:
        print("\nTrashing directories...\n")

    for dir_path in dirs:
        try:
            if os.listdir(dir_path):
                raise DirNotEmptyError("Directory not empty.")
            else:
                send2trash(dir_path)
        except OSError as ex:
            errors["directory"][dir_path] = str(ex)
        else:
            if args.verbose:
                print(f"{dir_path} trashed.")


for error_type, error_list in errors.items():
    if error_list:
        print(f"\n!!!! ==== {error_type.capitalize()} Errors ==== !!!!\n")
        print("Error processing the following paths:")
        for filepath, exception in error_list.items():
            print(f"{filepath} not processed due to exception: {exception}")
