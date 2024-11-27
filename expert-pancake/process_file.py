import os
import re
import time
from curlywaffle.main import get_unique_file_path
from exceptions import InvalidExtensionError, NoExtensionError
from settings import DATE_FORMAT, DATETIME_FORMAT, FILETYPES_FOR_YMDHMS_NAMING, IGNORE, YMD_PATTERN, YMDHMS_PATTERN
from shutil import move


class ProcessFile:
    def __init__(self, dest, exts_to_filetypes, og_path):
        """
        Set ext, og_basename, dest, filetype, and og_path properties.
        """
        self._full_dest = None
        self._modified_dt_object = None
        self._proposed_date_filename = None
        self._proposed_datetime_filename = None
        self._proposed_filename = None
        self._year = None
        _, self.ext = os.path.splitext(og_path)
        if not self.ext:
            raise NoExtensionError("No extension found.")
        self.filetype = exts_to_filetypes[self.ext.lower()]
        if self.filetype == IGNORE:
            raise InvalidExtensionError("Extension invalid.")
        self.og_basename = os.path.basename(og_path)
        self.dest = dest
        self.og_path = og_path
        self.ymd_match = re.match(YMD_PATTERN, self.og_basename)

    @property
    def full_dest(self) -> str:
        """
        The full destination directory for where the file will be saved.
        """
        if self._full_dest is None:
            self._full_dest = os.path.join(self.dest, self.year, self.filetype)
        return self._full_dest

    @property
    def modified_dt_object(self) -> time.struct_time:
        """
        The datetime object for when the file was last modified.
        """
        if self._modified_dt_object is None:
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
        return os.path.join(self.full_dest, self.proposed_filename)

    @property
    def proposed_date_filename(self):
        """
        The proposed filename in date format. Not necessarily used - see
        proposed_filename logic.
        """
        if self._proposed_date_filename is None:
            d = time.strftime(DATE_FORMAT, self.modified_dt_object)
            self._proposed_date_filename = f"{d}-{self.og_basename}"
        return self._proposed_date_filename

    @property
    def proposed_datetime_filename(self):
        """
        The proposed filename in datetime format. Not necessarily used - see
        proposed_filename logic.
        """
        if self._proposed_datetime_filename is None:
            dt = time.strftime(DATETIME_FORMAT, self.modified_dt_object)
            self._proposed_datetime_filename = f"{dt}{self.ext}"
        return self._proposed_datetime_filename

    @property
    def proposed_filename(self):
        """
        The proposed, potentially non-unique, filename for the file.
        """
        if self._proposed_filename is None:
            if self.filetype in FILETYPES_FOR_YMDHMS_NAMING:
                if re.search(YMDHMS_PATTERN, self.og_basename):
                    self._proposed_filename = self.og_basename
                else:
                    self._proposed_filename = self.proposed_datetime_filename
            elif self.ymd_match:
                self._proposed_filename = self.og_basename
            else:
                self._proposed_filename = self.proposed_date_filename
        return self._proposed_filename

    @property
    def year(self) -> str:
        """
        The year to which the file belongs; used for directory structure.
        """
        if self._year is None:
            if self.ymd_match:
                self._year = self.ymd_match.group("year")
            else:
                self._year = time.strftime("%Y", self.modified_dt_object)
        return self._year

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
