#!/usr/bin/env python3
"""
Migration status and test runner for pytest conversions.
"""
import os
import sys
from pathlib import Path
from collections import defaultdict
import subprocess


def count_test_files():
    """Count test files in both directories."""
    unittest_dir = Path("tests/unit_tests")
    pytest_dir = Path("tests_pytest/unit_tests")
    
    unittest_files = []
    pytest_files = []
    
    if unittest_dir.exists():
        for file_path in unittest_dir.rglob("*.py"):
            if file_path.name != "__init__.py" and not file_path.name.startswith("."):
                unittest_files.append(file_path)
    
    if pytest_dir.exists():
        for file_path in pytest_dir.rglob("*.py"):
            if file_path.name != "__init__.py" and not file_path.name.startswith("."):
                pytest_files.append(file_path)
    
    return unittest_files, pytest_files


def analyze_conversion_status():
    """Analyze the conversion status."""
    unittest_files, pytest_files = count_test_files()
    
    print("📊 PYTEST MIGRATION STATUS")
    print("=" * 50)
    print(f"Original unittest files: {len(unittest_files)}")
    print(f"Converted pytest files: {len(pytest_files)}")
    
    if unittest_files:
        completion_rate = (len(pytest_files) / len(unittest_files)) * 100
        print(f"Conversion progress: {completion_rate:.1f}%")
    
    print("\n📁 CONVERTED FILES:")
    if pytest_files:
        for file_path in sorted(pytest_files):
            rel_path = file_path.relative_to("tests_pytest/unit_tests")
            print(f"  ✅ {rel_path}")
    else:
        print("  (none yet)")
    
    print(f"\n📋 REMAINING FILES TO CONVERT: {len(unittest_files) - len(pytest_files)}")
    
    # Show a sample of remaining files
    converted_names = {f.stem for f in pytest_files}
    remaining = [f for f in unittest_files if f.stem not in converted_names]
    
    if remaining:
        print("Next files to consider:")
        for file_path in sorted(remaining)[:10]:  # Show first 10
            rel_path = file_path.relative_to("tests/unit_tests")
            print(f"  ⏳ {rel_path}")
        
        if len(remaining) > 10:
            print(f"  ... and {len(remaining) - 10} more")
    
    print("\n" + "=" * 50)
    return len(pytest_files) > 0


def run_pytest_tests(args=None):
    """Run pytest tests."""
    if not Path("tests_pytest").exists():
        print("❌ tests_pytest directory not found")
        return 1
    
    cmd = [sys.executable, "-m", "pytest", "tests_pytest/"]
    
    # Add common arguments
    if args and "--help" not in args:
        cmd.extend(["-v", "--tb=short"])
    
    # Add any provided arguments
    if args:
        cmd.extend(args)
    
    print("🧪 Running pytest tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 30)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⏸️  Test run interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def show_conversion_patterns():
    """Show key conversion patterns."""
    print("🔄 CONVERSION PATTERNS")
    print("=" * 50)
    
    patterns = [
        ("Test Classes", "unittest.TestCase", "class TestExample:"),
        ("Assertions", "self.assertEqual(a, b)", "assert a == b"),
        ("Exception Testing", "self.assertRaises(ValueError)", "pytest.raises(ValueError)"),
        ("Setup/Teardown", "setUp()/tearDown()", "@pytest.fixture"),
        ("Parametrized Tests", "subTest loops", "@pytest.mark.parametrize"),
        ("Test Markers", "(none)", "@pytest.mark.unit"),
    ]
    
    for category, unittest_code, pytest_code in patterns:
        print(f"\n{category}:")
        print(f"  unittest: {unittest_code}")
        print(f"  pytest:   {pytest_code}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            has_tests = analyze_conversion_status()
            return 0 if has_tests else 1
        
        elif command == "patterns":
            show_conversion_patterns()
            return 0
        
        elif command == "test":
            return run_pytest_tests(sys.argv[2:])
        
        elif command == "help":
            print("📚 Pytest Migration Helper")
            print("\nCommands:")
            print("  status    - Show conversion status")
            print("  patterns  - Show conversion patterns") 
            print("  test      - Run pytest tests")
            print("  help      - Show this help")
            print("\nExamples:")
            print("  python migration_helper.py status")
            print("  python migration_helper.py test")
            print("  python migration_helper.py test --unit-only")
            return 0
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python migration_helper.py help' for usage")
            return 1
    else:
        # Default: show status and run basic tests
        print("🚀 PYTEST MIGRATION HELPER\n")
        analyze_conversion_status()
        print("\n")
        
        if Path("tests_pytest").exists():
            return run_pytest_tests(["-q"])  # Quick test run
        return 0


if __name__ == "__main__":
    sys.exit(main())