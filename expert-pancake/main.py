import os
import pathlib

from dotenv import load_dotenv
from send2trash import send2trash
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


paths_to_trash = set()
for filepath in folder_to_process.rglob("*"):
    if os.path.isdir(filepath):
        paths_to_trash.add(filepath)
        continue

    ftp = FileToProcess(
        dest=destination_dir,
        exts_to_filetypes=exts_to_filetypes,
        og_path=filepath
    )

    ftp.create_dirs()
    new_filepath = ftp.move()
    print(f"{ftp.og_path} -> {new_filepath}")


for path_to_trash in paths_to_trash:
    if os.path.isdir(path_to_trash) and not len(os.listdir(path_to_trash)):
        send2trash(path_to_trash)