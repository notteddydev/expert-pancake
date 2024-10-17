import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

EXT_MAPPINGS_FILE = os.path.join(BASE_DIR, "extensions.json")

FILETYPES_FOR_YMDHMS_NAMING = {"videos", "photos"}

# Also matches strings such as '2020-02-31' which is obviously incorrect)
YMD_PATTERN = r'^(?P<year>\d{4})-(0[0-9]|1[0-2]|00)-(0[0-9]|[12][0-9]|3[01]|00)'
YMDHMS_PATTERN = r'^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (?:[01]\d|2[0-3])\.[0-5]\d\.[0-5]\d'
