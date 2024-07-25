import os
import re
import time

from curlywaffle.main import get_unique_file_path
from shutil import move

# Regex pattern matching date format: 'yyyy-MM-dd' (more or less; it matches strings such as '2020-02-31' which is obviously incorrect)
ymd_pattern = r'^(?P<year>\d{4})-(0[0-9]|1[0-2]|00)-(0[0-9]|[12][0-9]|3[01]|00)'
ymdhms_pattern = r'^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (?:[01]\d|2[0-3])\.[0-5]\d\.[0-5]\d'

class FileToProcess:
    def __init__(self, dest, exts_to_filetypes, og_path):
        _, self.ext = os.path.splitext(og_path)
        self.og_basename = os.path.basename(og_path)
        self.dest = dest
        self.filetype = exts_to_filetypes[self.ext]
        self.og_path = og_path

    @property
    def modified_datetime_object(self):
        modified_time_float = os.path.getmtime(self.og_path)
        modified_timestamp = time.ctime(modified_time_float)

        return time.strptime(modified_timestamp)
    
    @property
    def new_path(self):
        filename = self.og_basename
        filetypes_for_ymdhms_naming = {"photos", "videos"}
        
        if self.filetype in filetypes_for_ymdhms_naming and not re.search(ymdhms_pattern, self.og_basename):
            filename = f"{time.strftime('%Y-%m-%d %H.%M.%S', self.modified_datetime_object)}{self.ext}"
        
        if self.filetype not in filetypes_for_ymdhms_naming and not re.search(ymd_pattern, self.og_basename):
            filename = f"{time.strftime('%Y-%m-%d', self.modified_datetime_object)}-{self.og_basename}"

        return get_unique_file_path(f"{self.dest}/{self.year}/{self.filetype}/{filename}")

    @property
    def year(self):
        match = re.match(ymd_pattern, self.og_basename)

        return match.group("year") if match else time.strftime("%Y", self.modified_datetime_object)
    
    def create_dirs(self):
        year_dir = f"{self.dest}/{self.year}"
        filetype_dir = f"{year_dir}/{self.filetype}"
        mkdirs = [year_dir, filetype_dir]
        
        for mkdir in mkdirs:
            if not os.path.isdir(mkdir):
                os.mkdir(mkdir)

    def move(self):
        try:
            return move(self.og_path, self.new_path)
        except FileNotFoundError:
            print(f"FileNotFoundError when moving file with path: {self.og_path}")
