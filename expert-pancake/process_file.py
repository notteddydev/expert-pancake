import os
import re
import time
from curlywaffle.main import get_unique_file_path
from settings import FILETYPES_FOR_YMDHMS_NAMING, YMD_PATTERN, YMDHMS_PATTERN
from shutil import move


class ProcessFile:
    def __init__(self, dest, exts_to_filetypes, og_path):
        """
        Set ext, og_basename, dest, filetype, and og_path properties.
        """
        self._full_dest = None
        self._modified_dt_object = None
        _, self.ext = os.path.splitext(og_path)
        self.filetype = exts_to_filetypes[self.ext.lower()]
        self.og_basename = os.path.basename(og_path)
        self.dest = dest
        self.og_path = og_path
        self.ymd_match = re.match(YMD_PATTERN, self.og_basename)

    @property
    def full_dest(self) -> str:
        """
        The full destination directory for where the file will be saved.
        """
        if not self._full_dest:
            self._full_dest = os.path.join(self.dest, self.year, self.filetype)
        return self._full_dest

    @property
    def modified_dt_object(self) -> time.struct_time:
        """
        The datetime object for when the file was last modified.
        """
        if not self._modified_dt_object:
            modified_time_float = os.path.getmtime(self.og_path)
            modified_timestamp = time.ctime(modified_time_float)
            self._modified_dt_object = time.strptime(modified_timestamp)
        return self._modified_dt_object

    @property
    def new_path(self) -> str:
        """
        The new, unique, path to which the file will be saved.
        """
        return get_unique_file_path(self.new_path_if_no_duplicates)

    @property
    def new_path_if_no_duplicates(self):
        """
        The proposed, potentially non-unique, path for the file. Need to check
        that no file currently resides here.
        """
        filename = self.og_basename

        if self.filetype in FILETYPES_FOR_YMDHMS_NAMING:
            if not re.search(YMDHMS_PATTERN, self.og_basename):
                dt = time.strftime(
                    "%Y-%m-%d %H.%M.%S",
                    self.modified_dt_object,
                )
                filename = f"{dt}{self.ext}"
        elif not self.ymd_match:
            dt = time.strftime("%Y-%m-%d", self.modified_dt_object)
            filename = f"{dt}-{self.og_basename}"

        return os.path.join(self.full_dest, filename)

    @property
    def year(self) -> str:
        """
        The year to which the file belongs; used for directory structure.
        """
        if self.ymd_match:
            return self.ymd_match.group("year")

        return time.strftime("%Y", self.modified_dt_object)

    def __call__(self) -> str:
        """
        Move the existing file from its original path to self.new_path.
        """
        try:
            return move(self.og_path, self.new_path)
        except FileNotFoundError:
            print(
                f"FileNotFoundError when moving file with path: {self.og_path}"
            )
