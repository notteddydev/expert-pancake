import os
import re
import time
from exceptions import InvalidExtensionError, NoExtensionError
from settings import DATE_FORMAT, DATETIME_FORMAT, \
    FILETYPES_FOR_YMDHMS_NAMING, IGNORE, YMD_PATTERN, YMDHMS_PATTERN
from shutil import copy2, move


class ProcessFile:
    def __init__(self, dest, exts_to_filetypes, original_path, copyto_dest):
        """
        Set ext, original_stem, dest, filetype, and original_path properties.
        """
        self._filename = None
        self._filepath = None
        self._filepath_for_copy = None
        self._modified_dt_object = None
        self._moved_to = None
        self._new_path = None
        self._proposed_date_stem = None
        self._proposed_datetime_stem = None
        self._proposed_stem = None
        self._relative_dir = None
        self._year = None
        original_filename = os.path.basename(original_path)
        self.original_stem, self.ext = os.path.splitext(original_filename)
        if not self.ext:
            raise NoExtensionError("No extension found.")
        self.filetype = exts_to_filetypes[self.ext.lower()]
        if self.filetype == IGNORE:
            raise InvalidExtensionError("Extension invalid.")
        self.copyto_dest = copyto_dest
        self.dest = dest
        self.original_path = original_path
        self.ymd_match = re.match(YMD_PATTERN, self.original_stem)

    @property
    def filename(self) -> str:
        """
        The unique filename to which the file will be saved. Stem + ext.
        """
        if self._filename is None:
            self._filename = f"{self.unique_stem}{self.ext}"
        return self._filename

    @property
    def filepath(self) -> str:
        """
        The path to which the file will be saved.
        """
        if self._filepath is None:
            self._filepath = os.path.join(self.dest,
                                          self.relative_dir,
                                          self.filename,
                                          )
        return self._filepath

    @property
    def filepath_for_copy(self) -> str | None:
        """
        The path to which the file will be copied, or None if it will not be
        copied.
        """
        if self.copyto_dest is None:
            return None
        elif self._filepath_for_copy is None:
            self._filepath_for_copy = os.path.join(self.copyto_dest,
                                                   self.relative_dir,
                                                   self.filename,
                                                   )
        return self._filepath_for_copy

    @property
    def modified_dt_object(self) -> time.struct_time:
        """
        The datetime object for when the file was last modified.
        """
        if self._modified_dt_object is None:
            modified_time_float = os.path.getmtime(self.original_path)
            modified_timestamp = time.ctime(modified_time_float)
            self._modified_dt_object = time.strptime(modified_timestamp)
        return self._modified_dt_object

    @property
    def proposed_date_stem(self) -> str:
        """
        The proposed stem in date format. Not necessarily used - see
        proposed_stem logic.
        """
        if self._proposed_date_stem is None:
            d = time.strftime(DATE_FORMAT, self.modified_dt_object)
            self._proposed_date_stem = f"{d}-{self.original_stem}"
        return self._proposed_date_stem

    @property
    def proposed_datetime_stem(self) -> str:
        """
        The proposed stem in datetime format. Not necessarily used - see
        proposed_stem logic.
        """
        if self._proposed_datetime_stem is None:
            dt = time.strftime(DATETIME_FORMAT, self.modified_dt_object)
            self._proposed_datetime_stem = dt
        return self._proposed_datetime_stem

    @property
    def proposed_stem(self) -> str:
        """
        The proposed, potentially non-unique, stem for the file.
        """
        if self._proposed_stem is None:
            if self.filetype in FILETYPES_FOR_YMDHMS_NAMING:
                if re.search(YMDHMS_PATTERN, self.original_stem):
                    self._proposed_stem = self.original_stem
                else:
                    self._proposed_stem = self.proposed_datetime_stem
            elif self.ymd_match:
                self._proposed_stem = self.original_stem
            else:
                self._proposed_stem = self.proposed_date_stem
        return self._proposed_stem

    @property
    def relative_dir(self) -> str:
        """
        The directory path from the destination folder to the file.
        If dest is ~/Documents, and file is to be saved in
        ~/Documents/2000/photos, then 2000/photos is the relative_dir
        """
        if self._relative_dir is None:
            self._relative_dir = os.path.join(self.year, self.filetype)
        return self._relative_dir

    @property
    def relative_filepath(self) -> str:
        """
        The relative_dir + filename.
        """
        if self._relative_filepath is None:
            self._relative_filepath = os.path.join(self.relative_dir,
                                                   self.filename,
                                                   )
        return self._relative_filepath

    @property
    def unique_stem(self) -> str:
        """
        The proposed stem is taken, and checked against the destination for
        duplicates. If there are duplicates then stem-{duplicate_count}{ext}
        is returned.
        """
        stem = self.proposed_stem
        dest = f"{os.path.join(self.dest, self.relative_dir, stem)}{self.ext}"
        duplicate_count = 1

        while os.path.exists(dest):
            stem = f"{self.proposed_stem}-{duplicate_count}"
            joined = os.path.join(self.dest, self.relative_dir, stem)
            dest = f"{joined}{self.ext}"
            duplicate_count += 1

        return stem

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

    def make_dirs(self):
        """
        Make the directories that are need for the saving of the file, and if
        copying, the copied file.
        """
        os.makedirs(
            os.path.join(self.dest, self.relative_dir),
            exist_ok=True,
        )
        if self.copyto_dest is not None:
            os.makedirs(
                os.path.join(self.copyto_dest, self.relative_dir),
                exist_ok=True,
            )
        return

    def move(self) -> str:
        """
        Move the existing file from its original path to self.filepath.
        """
        self._moved_to = move(self.original_path, self.filepath)
        return self._moved_to

    def copy(self) -> str:
        """
        Copy the moved file, if moved, to self.filepath_for_copy
        """
        if self._moved_to is None:
            raise ValueError("No source path to copy the file from.")
        else:
            return copy2(self._moved_to, self.filepath_for_copy)
