#!/usr/bin/env python3
"""
Test runner for HTT preprocessor tests.
Runs all tests in the tests/ directory.
"""

import unittest
import sys
import os

# Add parent directory to path so we can import htt_preprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Discover and run all tests in the tests directory."""
    # Use standard unittest discovery
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run_all_tests()
