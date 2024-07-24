import os
import re
import time

# Regex pattern matching date format: 'yyyy-MM-dd' (more or less; it matches strings such as '2020-02-31' which is obviously incorrect)
pattern = r'^(?P<year>\d{4})-(0[0-9]|1[0-2]|00)-(0[0-9]|[12][0-9]|3[01]|00)'

class FileToProcess:
    def __init__(self, dest, exts_to_filetypes, original_path):
        _, self.ext = os.path.splitext(original_path)
        self.basename = os.path.basename(original_path)
        self.dest = dest
        self.filetype = exts_to_filetypes[self.ext]
        self.original_path = original_path
    
    @property
    def new_filepath(self):
        new_filepath = f"{self.dest}/{self.year}/{self.filetype}/{self.basename}"
        return new_filepath        

    @property
    def year(self):
        match = re.match(pattern, self.basename)

        if match:
            return match.group("year")
        
        modified_time_float = os.path.getmtime(self.original_path)
        modified_timestamp = time.ctime(modified_time_float)
        modified_datetime_object = time.strptime(modified_timestamp)

        return time.strftime("%Y", modified_datetime_object)
