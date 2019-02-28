#!/usr/bin/env python3
import argparse
import os
import sys
import datetime
import hashlib
import json
import another


def get_arguments():
    """
    Get argument from command-line interface
    Choose path with -p/--path option
    Choose show hidden or not with -s/--hidden option
    Choose different algorithm with -b/--bonus option
    - Expected value: ArgumentParser Object with 3 attribute:
        - parser.path
        - parser.hidden
        - parser.bonus
    """
    parser = argparse.ArgumentParser(description='Ahahehihohu')
    parser.add_argument('-p', '--path', type=str,
                        help='Root directory to start scanning \
                              for duplicate files')
    parser.add_argument('-s', '--hidden', action='store_true',
                        help='Show hidden files')
    parser.add_argument('-b', '--bonus', action='store_true',
                        help='Bonus: Using a better method')
    return parser.parse_args()


def valid_path(path):
    """
    Return True if exist path
    Exit program when path does not exist
    Write to error.log
    - Expected value: True
    - If path is unvalid or unable access with read method, write to
    error message to error.log and standard error, then exit program
    with exit code 1.
    """
    if os.path.exists(path) and os.access(path, os.R_OK):
        return True
    else:
        error_mes = ": ".join([str(os.path.basename(sys.argv[0])),
                              "valid_path", path, "Invalid path.\n"])
        with open('error.log', 'a+') as fd:
            fd.write("Time: " + str(datetime.datetime.now()) + "\n")
            fd.write(error_mes + "\n\n")
        sys.stderr.write(error_mes)
        sys.exit(1)


def file_valid(filename):
    """
    Check for readable file.
    - Expected value: True
    - Return False if unable access with by read method.
    """
    return os.access(filename, os.R_OK)


def scan_files(path, show_hidden=False):
    """
    Return list of files with full path
    - Expected value: list of files with full path
    - Return empty list if directory or files in directory unable to access
    """
    LIST_OF_FILES = list()
    for (dir_path, dir_names, file_names) in os.walk(path):
        if not show_hidden:
            file_names = [f for f in file_names if not f[0] == '.']
            dir_names[:] = [d for d in dir_names if not d[0] == '.']
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            try:
                if file_valid(file_path) and not os.path.islink(file_path):
                    full_path = os.path.realpath(file_path)
                    LIST_OF_FILES += [full_path]
            except OSError:
                continue
    return LIST_OF_FILES


def group_files_by_size(file_path_names):
    """
    Simple function group file by size
    - Expected value: list contain groups of files with the same size
    - Return empty list if unable to find group of files with the same size
    or group os files with size 0
    """
    RESULT_GROUP = list()
    GROUP_BY_SIZE = dict()
    for _file in file_path_names:
        stat = os.stat(_file)
        key = str(stat.st_size)
        if stat.st_size == 0:
            continue
        try:
            GROUP_BY_SIZE[key].append(_file)
        except KeyError:
            GROUP_BY_SIZE[key] = list()
            GROUP_BY_SIZE[key].append(_file)
    for _, values in GROUP_BY_SIZE.items():
        if len(values) > 1:
            RESULT_GROUP.append(list(value for value in values))
    return RESULT_GROUP


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_file_checksum(file_path_name):
    """Simple function get file checksum using chunk_reader"""
    h = hashlib.md5()
    if file_valid(file_path_name):
        with open(file_path_name, "rb") as fd:
            for chunk in chunk_reader(fd):
                h.update(chunk)
        return h.hexdigest()


def group_files_by_checksum(file_path_names):
    """
    Simple function group files by checksum
    - Expected value: list contain groups of files with the same hash
    - Return empty list if unable to find group of files with the same hash
    or group os files with size 0
    """
    RESULT_GROUP = list()
    GROUP_BY_CHECKSUM = dict()
    for _file in file_path_names:
        stat = os.stat(_file)
        key = get_file_checksum(_file)
        if stat.st_size == 0:
            continue
        if key:
            try:
                GROUP_BY_CHECKSUM[key].append(_file)
            except KeyError:
                GROUP_BY_CHECKSUM[key] = list()
                GROUP_BY_CHECKSUM[key].append(_file)
    for _, values in GROUP_BY_CHECKSUM.items():
        if len(values) > 1:
            RESULT_GROUP.append(list(value for value in values))
    return RESULT_GROUP


def find_duplicate_files(file_path_names):
    """
    Simple function find duplicate files
    Group files by size first and then
    group files by checksum using group_by function above
    """
    TMP = list()
    GROUP_BY_SIZE = group_files_by_size(file_path_names)
    if len(GROUP_BY_SIZE) > 0:
        for group in GROUP_BY_SIZE:
            for _file in group:
                TMP.append(_file)
    if len(TMP) > 0:
        return group_files_by_checksum(TMP)


def json_dump(data):
    """
    Return JSON formatted string
    """
    return json.dumps(data)


def main():
    """Main function operate program"""
    LIST_OF_FILES = []

    ARGS = get_arguments()
    PATH = ARGS.path
    SHOW_HIDDEN = ARGS.hidden
    BONUS = ARGS.bonus

    valid_path(PATH)

    LIST_OF_FILES = scan_files(PATH, SHOW_HIDDEN)
    if BONUS:
        RESULT = another.check_duplicates(LIST_OF_FILES)
    else:
        RESULT = find_duplicate_files(LIST_OF_FILES)

    if RESULT:
        print(json_dump(RESULT))
    else:
        print("This path have no duplicate files.")


if __name__ == '__main__':
    main()
