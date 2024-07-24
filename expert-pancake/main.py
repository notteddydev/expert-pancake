import os
import pathlib

from dotenv import load_dotenv
from send2trash import send2trash
from shutil import move
from tkinter.filedialog import askdirectory

from file_to_process import FileToProcess
from helpers import get_up_to_date_filetypes_and_their_exts

load_dotenv()

folder_to_process = pathlib.Path(os.environ.get('FOLDER_TO_PROCESS'))

if not os.path.isdir(folder_to_process):
    print("Folder to process does not exist. Not continuing.")
    exit()

destination_dir = askdirectory(
    initialdir=os.environ.get('SEARCH_FOR_DESTINATION_DIR_START_PATH'),
    title='Select Destination Folder'
)

if not len(destination_dir):
    print("Destination Folder not selected. Not continuing.")
    exit()

filetypes_and_their_exts = get_up_to_date_filetypes_and_their_exts(folder_to_process)
exts_to_filetypes = {ext: file_type for file_type, exts in filetypes_and_their_exts.items() for ext in exts}
filetypes = filetypes_and_their_exts.keys()
exts = [ext for exts in filetypes_and_their_exts.values() for ext in exts]

# Can I rename files prefixing them with the modification date before moving them?

# !!!!!!!!!!!! MAKE SURE YOU DO NOT OVERWRITE ANY EXISTING FILES / DIRS. TEST THIS LOCALLY
# BEFORE TESTING ON USB !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

paths_to_trash = set()
# Move all files to the base dir (folder_to_process).
# Add any directories to the paths_to_trash set.
for file_path in folder_to_process.rglob("*"):
    if os.path.isdir(file_path):
        paths_to_trash.add(file_path)
        continue

    ftp = FileToProcess(
        dest=destination_dir,
        exts_to_filetypes=exts_to_filetypes,
        original_path=file_path
    )
        
    print(ftp.new_filepath)