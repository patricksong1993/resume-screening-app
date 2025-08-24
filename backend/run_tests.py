#!/usr/bin/env python3
"""
Test runner for the Resume Screening Backend
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest"""
    print("🧪 Running tests for Resume Screening Backend...")
    print("=" * 50)
    
    try:
        # Run tests with pytest
        result = subprocess.run([
            "poetry", "run", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("\nTest Output:")
            print(result.stdout)
        else:
            print("❌ Some tests failed!")
            print("\nTest Output:")
            print(result.stdout)
            print("\nError Output:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Poetry not found. Please install Poetry first.")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
