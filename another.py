#!/usr/bin/env python3
import sys
import os
import hashlib
import logging
import json
from datetime import datetime


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.md5):
    """Get hash from file"""
    hashobj = hash()
    if os.access(filename, os.R_OK):
        with open(filename, 'rb') as file_object:
            if first_chunk_only:
                hashobj.update(file_object.read(1024))
            else:
                for chunk in chunk_reader(file_object):
                    hashobj.update(chunk)
            hashed = hashobj.hexdigest()
        return hashed


def group_by(file_path_names, hash=hashlib.md5, key='size'):
    """Group files by 3 optional:
    - By size
    - By 1024 first bytes
    - By full file content
    Choose: key = ['size', '1k', 'content'].
    Return a dictionary contain duplicate files with md5 as key
    """
    hashes_by = dict()

    for filename in file_path_names:
        try:
            if key == '1k':
                dict_key = get_hash(filename, first_chunk_only=True)
            elif key == 'content':
                dict_key = get_hash(filename, first_chunk_only=False)
            else:
                dict_key = os.path.getsize(filename)
        except OSError:
            continue
        duplicate = hashes_by.get(dict_key)
        if duplicate:
            hashes_by[dict_key].append(filename)
        else:
            hashes_by[dict_key] = []
            hashes_by[dict_key].append(filename)

    return hashes_by


def create_log_file(LOG_FILENAME='default.log'):
    """
    Create log file
    """
    logging.basicConfig(
        filename=LOG_FILENAME,
        level=logging.DEBUG,
        format='%(message)s'
    )


def check_duplicates(file_path_names, hash=hashlib.md5):
    """
    Return a list of duplicate files
    """
    result = []
    hashes_by_size = dict()
    hashes_on_1k = dict()
    hashes_full = dict()

    create_log_file("another.log")

    # hashes_by_size = group_by_size(file_path_names)
    hashes_by_size = group_by(file_path_names, key='size')

    logging.debug("Time: " + str(datetime.now()))
    logging.debug("List hashes by size:")
    logging.debug(json.dumps(hashes_by_size, indent=4))

    for keys, values in hashes_by_size.items():
        if len(values) < 2:
            continue
        else:
            # hashes_on_1k.update(group_on_1k(values))
            hashes_on_1k.update(group_by(values, key='1k'))

    logging.debug("List hashes on 1k:")
    logging.debug(json.dumps(hashes_on_1k, indent=4))

    for keys, values in hashes_on_1k.items():
        if len(values) < 2:
            continue
        else:
            # hashes_full.update(group_by_content(values))
            hashes_full.update(group_by(values, key='content'))

    logging.debug("List hashes by full content:")
    logging.debug(json.dumps(hashes_full, indent=4))

    for keys, values in hashes_full.items():
        if len(values) < 2:
            continue
        else:
            result.append(values)

    logging.debug("Result list:")
    logging.debug(json.dumps(result, indent=4))
    logging.debug('<===============================END-OF-MESSAGE\
===============================>\n')

    return result
