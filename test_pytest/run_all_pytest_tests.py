#!/usr/bin/env python3
"""
Run all pytest tests for the Omni-Converter.

This script runs all the pytest test modules and outputs results to both console and JSON files.
This is the pytest equivalent of tests/run_all_tests.py
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_pytest_tests():
    """Run all the pytest test modules and collect results."""
    # Make sure the collected_results directory exists
    results_dir = Path('test_pytest/collected_results')
    results_dir.mkdir(parents=True, exist_ok=True)

    # Change directory to project root to ensure correct paths
    project_root = Path(__file__).parent.parent  # Go up one level from test_pytest
    os.chdir(project_root)
    
    # Add project root to Python path to ensure imports work
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    print("Running all pytest tests...\n")

    # Run pytest with JSON report
    pytest_args = [
        sys.executable, '-m', 'pytest',
        'test_pytest/',
        '-v',
        '--tb=short',
        '--json-report',
        f'--json-report-file={results_dir}/pytest_report.json'
    ]

    try:
        result = subprocess.run(pytest_args, capture_output=True, text=True)
        
        # Print stdout and stderr
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Load and process the JSON report if it exists
        json_report_file = results_dir / 'pytest_report.json'
        if json_report_file.exists():
            with open(json_report_file, 'r') as f:
                pytest_report = json.load(f)
            
            # Generate summary report
            summary = {
                'timestamp': datetime.now().isoformat(),
                'tests_run': len(pytest_report.get('tests', [])),
                'passed': len([t for t in pytest_report.get('tests', []) if t['outcome'] == 'passed']),
                'failed': len([t for t in pytest_report.get('tests', []) if t['outcome'] == 'failed']),
                'skipped': len([t for t in pytest_report.get('tests', []) if t['outcome'] == 'skipped']),
                'errors': len([t for t in pytest_report.get('tests', []) if t['outcome'] == 'error']),
                'duration': pytest_report.get('duration', 0),
                'success': result.returncode == 0
            }
        else:
            # Fallback summary if JSON report is not available
            summary = {
                'timestamp': datetime.now().isoformat(),
                'tests_run': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0,
                'duration': 0,
                'success': result.returncode == 0
            }

        # Save summary to JSON
        with open(results_dir / 'pytest_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        print("\nPytest Test Summary:")
        print(f"Tests run: {summary['tests_run']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Errors: {summary['errors']}")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Success: {summary['success']}")
        print(f"\nDetailed results saved to {results_dir}/pytest_report.json")
        print(f"Summary saved to {results_dir}/pytest_summary.json")

        return result.returncode

    except Exception as e:
        print(f"Error running pytest: {e}")
        return 1


def run_specific_markers():
    """Run tests with specific markers separately."""
    markers = ['unit', 'integration', 'performance', 'slow']
    results_dir = Path('test_pytest/collected_results')
    
    for marker in markers:
        print(f"\n{'='*50}")
        print(f"Running tests with marker: {marker}")
        print(f"{'='*50}")
        
        pytest_args = [
            sys.executable, '-m', 'pytest',
            'test_pytest/',
            '-v',
            '-m', marker,
            '--json-report',
            f'--json-report-file={results_dir}/pytest_report_{marker}.json'
        ]
        
        try:
            result = subprocess.run(pytest_args, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        except Exception as e:
            print(f"Error running {marker} tests: {e}")


if __name__ == "__main__":
    # Install pytest-json-report if not available
    try:
        import pytest_json_report
    except ImportError:
        print("Installing pytest-json-report...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest-json-report'])

    # Run all tests
    exit_code = run_pytest_tests()
    
    # Run tests by marker if requested
    if '--by-markers' in sys.argv:
        run_specific_markers()
    
    sys.exit(exit_code)