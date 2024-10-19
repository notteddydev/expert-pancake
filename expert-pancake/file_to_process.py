import os
import re
import time
from curlywaffle.main import get_unique_file_path
from settings import FILETYPES_FOR_YMDHMS_NAMING, YMD_PATTERN, YMDHMS_PATTERN
from shutil import move


class FileToProcess:
    def __init__(self, dest, exts_to_filetypes, og_path):
        """
        Set ext, og_basename, dest, filetype, and og_path properties.
        """
        _, self.ext = os.path.splitext(og_path)
        self.og_basename = os.path.basename(og_path)
        self.dest = dest
        self.filetype = exts_to_filetypes[self.ext.lower()]
        self.og_path = og_path

    @property
    def full_dest(self) -> str:
        """
        The full destination directory for where the file will be saved.
        """
        return os.path.join(self.dest, self.year, self.filetype)

    @property
    def modified_dt_object(self) -> time.struct_time:
        """
        The datetime object for when the file was last modified.
        """
        modified_time_float = os.path.getmtime(self.og_path)
        modified_timestamp = time.ctime(modified_time_float)
        return time.strptime(modified_timestamp)

    @property
    def new_path(self) -> str:
        """
        The new, unique, path to which the file will be saved.
        """
        filename = self.og_basename

        if self.filetype in FILETYPES_FOR_YMDHMS_NAMING:
            if not re.search(YMDHMS_PATTERN, self.og_basename):
                dt = time.strftime(
                    "%Y-%m-%d %H.%M.%S",
                    self.modified_dt_object,
                )
                filename = f"{dt}{self.ext}"
        elif not re.search(YMD_PATTERN, self.og_basename):
            dt = time.strftime("%Y-%m-%d", self.modified_dt_object)
            filename = f"{dt}-{self.og_basename}"

        return get_unique_file_path(os.path.join(self.full_dest, filename))

    @property
    def year(self) -> str:
        """
        The year to which the file belongs; used for directory structure.
        """
        if match := re.match(YMD_PATTERN, self.og_basename):
            return match.group("year")

        return time.strftime("%Y", self.modified_dt_object)

    def move(self) -> str:
        """
        Move the existing file from its original path to self.new_path.
        """
        try:
            return move(self.og_path, self.new_path)
        except FileNotFoundError:
            print(
                f"FileNotFoundError when moving file with path: {self.og_path}"
            )
