#!/usr/bin/env python3
import unittest
import os
import json
import find_duplicate_files as fdf

from subprocess import Popen, PIPE, run


class ScanFilesTest(unittest.TestCase):
    def setUp(self):
        # Setup the environment
        self.DIR_NAME = 'this_is_test_directory_name'
        process = Popen(['./generate_duplicate_files.py',
                         '--file-count', '5',
                         '--duplicate-file-ratio', '1',
                         '-p', self.DIR_NAME],
                        stdout=PIPE)
        obj = process.communicate()[0].decode()
        obj = json.loads(obj)
        self.duplicate_files = [out[0] for out in obj]

    def tearDown(self):
        # Remove the environment
        run(['rm', '-rf', self.DIR_NAME])

    def test_symlink_not_in_result(self):
        # Check symlink not in result list
        # result should just contain only on file without any symlinks
        result = fdf.scan_files('./TEST_DIR/symlink_test')
        expected = [os.path.join(os.getcwd(),
                    'TEST_DIR/symlink_test/test_file1')]
        self.assertEqual(result, expected)

    def test_empty_dir(self):
        # Check scan an empty directory
        # Should return an empty list
        result = fdf.scan_files('./TEST_DIR/empty_dir')
        expected = []
        self.assertEqual(result, expected)

    def test_file_instead_dir(self):
        # Check scan a file instead of directory
        # Should return an empty list
        result = fdf.scan_files('./TEST_DIR/test_file')
        expected = []
        self.assertEqual(result, expected)

    def test_scan_non_exist_path(self):
        # Check scan a non-exist path
        # Should return an empty list
        result = fdf.scan_files('./TEST_DIR/non_exist_path')
        expected = []
        self.assertEqual(result, expected)

    def test_normal_scan(self):
        # Check normal scan a path
        # Should return a list as expected
        expected = sorted([os.path.join(os.getcwd(), out)
                          for out in self.duplicate_files])
        result = sorted(fdf.scan_files(self.DIR_NAME))
        self.assertListEqual(result, expected)


class GroupFilesBySizeTest(unittest.TestCase):
    def setUp(self):
        # Setup the environment
        self.DIR_NAME = 'this_is_test_directory_name'
        process = Popen(['./generate_duplicate_files.py',
                         '--file-count', '5',
                         '--duplicate-file-ratio', '1',
                         '-p', self.DIR_NAME],
                        stdout=PIPE)
        obj = process.communicate()[0].decode()
        obj = json.loads(obj)
        self.duplicate_files = [os.path.realpath(out[0]) for out in obj]
        self.LIST_OF_FILES = fdf.scan_files('.')

    def tearDown(self):
        # Remove the environment
        run(['rm', '-rf', self.DIR_NAME])

    def test_normal_group_by_size(self):
        # Change group in result to set for comparision
        result = [set(group) for group in
                  fdf.group_files_by_size(self.LIST_OF_FILES)]
        # Duplicate files should be in result list
        expected = set(self.duplicate_files)
        self.assertIn(expected, result)

    def test_empty_file_not_in_result(self):
        # Empty file should not be in result
        result = fdf.group_files_by_size(self.LIST_OF_FILES)
        expected1 = os.path.join(os.getcwd(), 'TEST_DIR/testcase/empty_file1')
        expected2 = os.path.join(os.getcwd(), 'TEST_DIR/testcase/empty_file2')
        for n, group in enumerate(result):
            self.assertNotIn(expected1, result)
            self.assertNotIn(expected2, result)


class GroupFilesByChecksumTest(unittest.TestCase):
    def setUp(self):
        # Setup the environment
        self.DIR_NAME = 'this_is_test_directory_name'
        process = Popen(['./generate_duplicate_files.py',
                         '--file-count', '5',
                         '--duplicate-file-ratio', '1',
                         '-p', self.DIR_NAME],
                        stdout=PIPE)
        obj = process.communicate()[0].decode()
        obj = json.loads(obj)
        self.duplicate_files = [out[0] for out in obj]
        self.LIST_OF_FILES = fdf.scan_files('.')

    def tearDown(self):
        # Remove the environment
        run(['rm', '-rf', self.DIR_NAME])

    def test_normal_group_by_checksum(self):
        group_files = fdf.group_files_by_checksum(self.duplicate_files)
        result = [set(group) for group in group_files]
        expected = set(self.duplicate_files)
        # Group of duplicated files should be in result
        self.assertIn(expected, result)


class FindDuplicateFilesTest(unittest.TestCase):
    def setUp(self):
        # Setup the environment
        self.DIR_NAME = 'this_is_test_directory_name'
        process = Popen(['./generate_duplicate_files.py',
                         '--file-count', '5',
                         '--duplicate-file-ratio', '1',
                         '-p', self.DIR_NAME],
                        stdout=PIPE)
        obj = process.communicate()[0].decode()
        obj = json.loads(obj)
        self.duplicate_files = [out[0] for out in obj]
        self.LIST_OF_FILES = fdf.scan_files('.')

    def tearDown(self):
        # Remove the environment
        run(['rm', '-rf', self.DIR_NAME])

    def test_find_duplicate_files(self):
        # Create empty file for test
        add_file = [os.path.join(os.getcwd(), 'TEST_DIR/testcase/empty_file1')]
        dup_files = fdf.find_duplicate_files(self.duplicate_files + add_file)
        result = [set(group) for group in dup_files]
        expected = set(self.duplicate_files)
        # Group of duplicated files should be in result
        self.assertIn(expected, result)
        # Empty file should not be in result
        self.assertNotIn(add_file, result)
