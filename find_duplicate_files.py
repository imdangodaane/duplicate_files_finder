#!/bin/bash/env python3
import argparse
import os
import sys
import datetime
import hashlib
import json


def get_arguments():
    parser = argparse.ArgumentParser(description='Ahahehihohu')
    parser.add_argument('-p', '--path', type=str, 
                        help='Root directory to start scanning for duplicate files')
    parser.add_argument('-i', '--hidden', action='store_true',
                        help='Show hidden files')
    return parser.parse_args()


def path_valid(path):
    if os.path.exists(path):
        return True
    else:
        error_log = ": ".join([str(os.path.basename(sys.argv[0])), "path_valid", path, "Invalid path.\n"])
        with open('error.log', 'a+') as fd:
            fd.write("Time: " + str(datetime.datetime.now()) + "\n")
            fd.write(error_log + "\n\n")
        sys.stderr.write(error_log)
        sys.exit(1)


def scan_files(path, show_hidden):
    if path_valid(path):
        list_of_files = list()
        for (dir_path, dir_names, file_names) in os.walk(path):
            if not show_hidden:
                file_names = [f for f in file_names if not f[0] == '.']
                dir_names[:] = [d for d in dir_names if not d[0] == '.']
            for file_name in file_names:
                if not os.path.islink(os.path.join(dir_path, file_name)):
                    list_of_files += [os.path.join(dir_path, file_name)]
        return list_of_files


def group_files_by_size(file_path_names):
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
        # temp = list()
        # for value in values:
        #     temp.append(value)
        # result_group.append(temp)
    return result_group


def get_file_checksum(file_path_name):
    if path_valid(file_path_name):
        with open(file_path_name, "rb") as fd:
            content = fd.read()
            h = hashlib.md5()
            h.update(content)
        return h.hexdigest()


def group_files_by_checksum(file_path_names):
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
    tmp = list()
    group_by_size = group_files_by_size(file_path_names)
    if len(group_by_size) > 0:
        for group in group_by_size:
            for _file in group:
                tmp.append(_file)
    if len(tmp) > 0:
        return group_files_by_checksum(tmp)


def json_dump(data):
    return json.dumps(data)


def main():
    args = get_arguments()
    path = args.path
    show_hidden = args.hidden
    list_of_files = scan_files(path, show_hidden)
    # print(list_of_files)
    # group_by_size = group_files_by_size(list_of_files)
    # group_by_checksum = group_files_by_checksum(list_of_files)
    # print(group_by_size)
    # print(group_by_checksum)
    result = find_duplicate_files(list_of_files)
    print(result)
    print(type(result))
    print(json_dump(result))
    print(type(json_dump(result)))


if __name__ == '__main__':
    main()
