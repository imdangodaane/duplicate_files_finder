#!/bin/bash/env python3
import argparse
import os
import sys
import datetime
import pprint


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
    print(group_by_size)
    for keys, values in group_by_size.items():
        print(keys)
        print(values)
        result_group.append(list([values]))
    return group_by_size


def main():
    args = get_arguments()
    path = args.path
    show_hidden = args.hidden
    list_of_files = scan_files(path, show_hidden)
    print(list_of_files)
    group_by_size = group_files_by_size(list_of_files)
    print(group_by_size)


if __name__ == '__main__':
    main()
