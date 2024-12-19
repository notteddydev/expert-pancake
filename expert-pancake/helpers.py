import os
import re
import time
from settings import DATE_FORMAT, DATETIME_FORMAT, \
    FILETYPES_FOR_YMDHMS_NAMING, YMDHMS_PATTERN


def get_dest_filename(dest, relative_dir, original_stem, ext,
                      filetype, modified_dt_obj, ymd_match):
    proposed_stem = get_proposed_stem(filetype=filetype,
                                      original_stem=original_stem,
                                      modified_dt_obj=modified_dt_obj,
                                      ymd_match=ymd_match)
    unique_stem = get_unique_stem(dest=dest,
                                  relative_dir=relative_dir,
                                  proposed_stem=proposed_stem,
                                  ext=ext)
    return f"{unique_stem}{ext}"


def get_modified_dt_obj(original_path):
    modified_time_float = os.path.getmtime(original_path)
    modified_timestamp = time.ctime(modified_time_float)
    return time.strptime(modified_timestamp)


def get_proposed_date_stem(original_stem, modified_dt_obj) -> str:
    """
    The proposed stem in date format. Not necessarily used - see
    proposed_stem logic.
    """
    d = time.strftime(DATE_FORMAT, modified_dt_obj)
    return f"{d}-{original_stem}"


def get_proposed_datetime_stem(modified_dt_obj) -> str:
    """
    The proposed stem in datetime format. Not necessarily used - see
    proposed_stem logic.
    """
    dt = time.strftime(DATETIME_FORMAT, modified_dt_obj)
    return dt


def get_proposed_stem(filetype, original_stem, modified_dt_obj, ymd_match) -> str:
    """
    The proposed, potentially non-unique, stem for the file.
    """
    if filetype in FILETYPES_FOR_YMDHMS_NAMING:
        if re.search(YMDHMS_PATTERN, original_stem):
            return original_stem
        else:
            return get_proposed_datetime_stem(modified_dt_obj)
    elif ymd_match:
        return original_stem
    else:
        return get_proposed_date_stem(original_stem, modified_dt_obj)


def get_unique_stem(dest, relative_dir, proposed_stem, ext):
    """
    The proposed stem is taken, and checked against the destination for
    duplicates. If there are duplicates then stem-{duplicate_count}{ext}
    is returned.
    """
    stem = proposed_stem
    dest = f"{os.path.join(dest, relative_dir, stem)}{ext}"
    duplicate_count = 1

    while os.path.exists(dest):
        stem = f"{proposed_stem}-{duplicate_count}"
        joined = os.path.join(dest, relative_dir, stem)
        dest = f"{joined}{ext}"
        duplicate_count += 1

    return stem


def process_file(src_filepath, dest_filename, relative_dir, dest_parent, fn,
                 verbose):
    os.makedirs(os.path.join(dest_parent, relative_dir), exist_ok=True)
    dest_filepath = os.path.join(dest_parent, relative_dir, dest_filename)
    res = fn(src_filepath, dest_filepath)
    print(f"{verbose}: {src_filepath} -> {dest_filepath}")
    return res
