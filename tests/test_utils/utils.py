#!/usr/bin/env python3
"""
Base test class for HTT preprocessor tests.
Provides utilities for creating temporary test files and running the preprocessor.
"""

import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path
import tempfile
from typing import Optional

# Add parent directory to path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crowbar import CrowbarPreprocessor, Fpath


def slurp(fname: Fpath, encoding="utf-8") -> str:
    """Read entire file into string."""
    with open(fname, "r", encoding=encoding) as fh:
        return fh.read()


class WithNamedTempFile:
    def __init__(self, prefix: Optional[str] = None, suffix: str = ".tmp"):
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, text=True)
        os.close(fd)
        self.__path = Path(path)

    @property
    def path(self) -> Path:
        return self.__path

    def __enter__(self) -> "WithNamedTempFile":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__path.unlink(missing_ok=True)


class HTTTestBase(unittest.TestCase):
    """Base class for HTT preprocessor tests."""

    def setUp(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp(prefix="htt_test_")
        self.processor = CrowbarPreprocessor()
        self.maxDiff = None

    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename, content):
        """Create a test file with given content in the temp directory."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def create_python_file(self, filename, content):
        """Create a Python file with given content in the temp directory."""
        return self.create_test_file(filename, content)

    def run_preprocessor(self, input_file, output_file=None):
        """Run the preprocessor on the input file."""
        if output_file is None:
            output_file = input_file  # In-place processing

        # Change to temp directory so supporting files can be found
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            self.processor.process_file(input_file, output_file)
        finally:
            os.chdir(original_cwd)

        # Read the result
        with open(output_file, "r", encoding="utf-8") as f:
            return f.read()

    def assert_preprocessor_output(
        self,
        input_content,
        expected_output,
        input_filename="test_input.py",
        supporting_files=None,
    ):
        """
        Test that the preprocessor produces expected output.

        Args:
            input_content: Content of the main input file
            expected_output: Expected output after preprocessing
            input_filename: Name of the input file (default: test_input.py)
            supporting_files: Dict of {filename: content} for additional files
        """
        # Create supporting files if provided
        if supporting_files:
            for filename, content in supporting_files.items():
                self.create_test_file(filename, content)

        # Create input file
        input_file = self.create_test_file(input_filename, input_content)

        # Run preprocessor
        actual_output = self.run_preprocessor(input_file)

        # Assert output matches expected
        self.assertEqual(actual_output, expected_output)

    def assert_preprocessor_error(
        self, input_content, expected_error_pattern=None, input_filename="test_input.py"
    ):
        """
        Test that the preprocessor raises an expected error.

        Args:
            input_content: Content of the input file
            expected_error_pattern: Regex pattern to match in error message
            input_filename: Name of the input file
        """
        input_file = self.create_test_file(input_filename, input_content)

        with self.assertRaises(Exception) as context:
            self.run_preprocessor(input_file)

        if expected_error_pattern:
            self.assertRegex(str(context.exception), expected_error_pattern)
