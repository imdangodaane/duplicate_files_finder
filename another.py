#!/bin/bash/env python3
import sys
import os
import hashlib
import logging
from datetime import datetime


LOG_FILENAME = 'another_module_error.log'
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    format='%(message)s'
)


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
    Choose: key = ['size', '1k', 'content']
    Return a dictionary contain duplicate files with md5 as key
    """
    hashes_by = dict()

    for filename in file_path_names:
        try:
            if key == 'size':
                dict_key = os.path.getsize(filename)
            elif key == '1k':
                dict_key = get_hash(filename, first_chunk_only=True)
            elif key == 'content':
                dict_key = get_hash(filename, first_chunk_only=False)
        except OSError:
            continue
        duplicate = hashes_by.get(dict_key)
        if duplicate:
            hashes_by[dict_key].append(filename)
        else:
            hashes_by[dict_key] = []
            hashes_by[dict_key].append(filename)

    return hashes_by


# def group_by_size(file_path_names):
#     hashes_by_size = dict()

#     for filename in file_path_names:
#         try:
#             file_size = os.path.getsize(filename)
#         except OSError:
#             continue
#         duplicate = hashes_by_size.get(file_size)
#         if duplicate:
#             hashes_by_size[file_size].append(filename)
#         else:
#             hashes_by_size[file_size] = []
#             hashes_by_size[file_size].append(filename)

#     return hashes_by_size


# def group_on_1k(file_path_names, hash=hashlib.md5):
#     hashes_on_1k = dict()

#     for filename in file_path_names:
#         try:
#             small_hash = get_hash(filename, first_chunk_only=True)
#         except OSError:
#             continue
#         duplicate = hashes_on_1k.get(small_hash)
#         if duplicate:
#             hashes_on_1k[small_hash].append(filename)
#         else:
#             hashes_on_1k[small_hash] = []
#             hashes_on_1k[small_hash].append(filename)
#     return hashes_on_1k


# def group_by_content(file_path_names, hash=hashlib.md5):
#     hashes_full = dict()

#     for filename in file_path_names:
#         try:
#             full_hash = get_hash(filename, first_chunk_only=False)
#         except OSError:
#             continue
#         duplicate = hashes_full.get(full_hash)
#         if duplicate:
#             hashes_full[full_hash].append(filename)
#         else:
#             hashes_full[full_hash] = []
#             hashes_full[full_hash].append(filename)

#     return hashes_full


def check_duplicates(file_path_names, hash=hashlib.md5):
    """
    Return a list of duplicate files
    """
    result = []
    hashes_by_size = dict()
    hashes_on_1k = dict()
    hashes_full = dict()

    # hashes_by_size = group_by_size(file_path_names)
    hashes_by_size = group_by(file_path_names, key='size')

    logging.debug("Time: " + str(datetime.now()))
    logging.debug("List hashes by size:")
    logging.debug(hashes_by_size)

    for keys, values in hashes_by_size.items():
        if len(values) < 2:
            continue
        else:
            # hashes_on_1k.update(group_on_1k(values))
            hashes_on_1k.update(group_by(values, key='1k'))

    logging.debug("List hashes on 1k:")
    logging.debug(hashes_on_1k)

    for keys, values in hashes_on_1k.items():
        if len(values) < 2:
            continue
        else:
            # hashes_full.update(group_by_content(values))
            hashes_full.update(group_by(values, key='content'))

    logging.debug("List hashes by full content:")
    logging.debug(hashes_full)

    for keys, values in hashes_full.items():
        if len(values) < 2:
            continue
        else:
            result.append(values)

    logging.debug("Result list:")
    logging.debug(result)
    logging.debug('<===============================END-OF-MESSAGE\
                  ===============================>\n')

    return result
