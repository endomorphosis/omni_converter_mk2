#!/usr/bin/env python3
"""
Test runner for the pytest test suite.
This script provides a convenient way to run all pytest tests with proper configuration.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run pytest with specified arguments."""
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test path
    cmd.append("tests_pytest/")
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add specific test markers
    if args.unit_only:
        cmd.extend(["-m", "unit"])
    elif args.integration_only:
        cmd.extend(["-m", "integration"])
    elif args.no_slow:
        cmd.extend(["-m", "not slow"])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Add any additional arguments
    if args.extra_args:
        cmd.extend(args.extra_args.split())
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run pytest tests for omni_converter_mk2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pytest_tests.py                  # Run all tests
  python run_pytest_tests.py --unit-only      # Run only unit tests
  python run_pytest_tests.py --no-slow        # Skip slow tests
  python run_pytest_tests.py --verbose        # Verbose output
  python run_pytest_tests.py --coverage       # Run with coverage report
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--unit-only",
        action="store_true", 
        help="Run only unit tests"
    )
    
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests"
    )
    
    parser.add_argument(
        "--no-slow",
        action="store_true",
        help="Skip tests marked as slow"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    
    parser.add_argument(
        "--extra-args",
        help="Additional arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("Error: pytest is not installed. Run 'pip install pytest pytest-mock' first.")
        return 1
    
    # Check if tests_pytest directory exists
    test_dir = Path("tests_pytest")
    if not test_dir.exists():
        print(f"Error: Test directory '{test_dir}' does not exist.")
        return 1
    
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())