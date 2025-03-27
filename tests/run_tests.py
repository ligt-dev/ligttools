"""
Run all tests for the LigtTools package.
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests.test_converters import main as test_converters
from tests.test_cli import main as test_cli


def main():
    """Run all tests."""
    print("Running converter tests...")
    test_converters()
    
    print("\nRunning CLI tests...")
    test_cli()
    
    print("\nAll tests passed successfully!")


if __name__ == "__main__":
    main()