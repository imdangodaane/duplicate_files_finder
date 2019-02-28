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
    """Check for readable file"""
    return os.access(filename, os.R_OK)


def scan_files(path, show_hidden=False):
    """Return list of files of path"""
    list_of_files = list()
    for (dir_path, dir_names, file_names) in os.walk(path):
        if not show_hidden:
            file_names = [f for f in file_names if not f[0] == '.']
            dir_names[:] = [d for d in dir_names if not d[0] == '.']
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            try:
                if file_valid(file_path) and not os.path.islink(file_path):
                    full_path = os.path.realpath(file_path)
                    list_of_files += [full_path]
            except OSError:
                continue
    return list_of_files


def group_files_by_size(file_path_names):
    """Simple function group file by size"""
    result_group = list()
    group_by_size = dict()
    for _file in file_path_names:
        stat = os.stat(_file)
        key = str(stat.st_size)
        if stat.st_size == 0:
            continue
        try:
            group_by_size[key].append(_file)
        except KeyError:
            group_by_size[key] = list()
            group_by_size[key].append(_file)
    for keys, values in group_by_size.items():
        if len(values) > 1:
            result_group.append(list(value for value in values))
    return result_group


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_file_checksum(file_path_name):
    """Simple function get file checksum"""
    h = hashlib.md5()
    if file_valid(file_path_name):
        with open(file_path_name, "rb") as fd:
            for chunk in chunk_reader(fd):
                h.update(chunk)
        return h.hexdigest()


def group_files_by_checksum(file_path_names):
    """Simple function group files by checksum"""
    result_group = list()
    group_by_checksum = dict()
    for _file in file_path_names:
        stat = os.stat(_file)
        key = get_file_checksum(_file)
        if stat.st_size == 0:
            continue
        if key:
            try:
                group_by_checksum[key].append(_file)
            except KeyError:
                group_by_checksum[key] = list()
                group_by_checksum[key].append(_file)
    for keys, values in group_by_checksum.items():
        if len(values) > 1:
            result_group.append(list(value for value in values))
    return result_group


def find_duplicate_files(file_path_names):
    """
    Simple function find duplicate files
    Group files by size first and then
    group files by checksum using group_by function above
    """
    tmp = list()
    group_by_size = group_files_by_size(file_path_names)
    if len(group_by_size) > 0:
        for group in group_by_size:
            for _file in group:
                tmp.append(_file)
    if len(tmp) > 0:
        return group_files_by_checksum(tmp)


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
    LIST_OF_FILES = scan_files(PATH)
    if BONUS:
        RESULT = another.check_duplicates(LIST_OF_FILES)
    else:
        group_by_size = group_files_by_size(LIST_OF_FILES)
        group_by_checksum = group_files_by_checksum(LIST_OF_FILES)
        RESULT = find_duplicate_files(LIST_OF_FILES)
    print(json_dump(RESULT))


if __name__ == '__main__':
    main()
