#!/usr/bin/env python3
"""
Test script for the Flatten tool.
Tests both local directory and GitHub repository functionality.
"""

import sys
import traceback
from pathlib import Path

from Siphon.ingestion.github.flatten_directory import flatten_directory
from Siphon.ingestion.github.flatten_url import flatten_github_repo


def test_local_directory():
    """Test flattening the current directory (local use case)."""
    print("=" * 60)
    print("TESTING LOCAL DIRECTORY FLATTENING")
    print("=" * 60)
    print(f"Target: Current directory ({Path.cwd()})")
    print()

    try:
        result = flatten_directory(".")

        # Basic validation
        if not result:
            print("❌ ERROR: No output generated")
            return False

        if not result.startswith("<?xml"):
            print("❌ ERROR: Output doesn't appear to be XML")
            return False

        if "<project name=" not in result:
            print("❌ ERROR: Missing project element")
            return False

        if "<directory_tree>" not in result:
            print("❌ ERROR: Missing directory_tree element")
            return False

        if "<file_contents>" not in result:
            print("❌ ERROR: Missing file_contents element")
            return False

        print("✅ SUCCESS: Local directory flattening completed")
        print(f"📊 Output length: {len(result)} characters")

        # Count some elements for validation
        file_count = result.count("<file ")
        cdata_count = result.count("<![CDATA[")
        print(f"📁 Files found: {file_count}")
        print(f"📄 CDATA sections: {cdata_count}")

        # Show a snippet of the output
        print("\n--- SAMPLE OUTPUT (first 500 chars) ---")
        print(result[:500] + "..." if len(result) > 500 else result)
        print("--- END SAMPLE ---")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False


def test_github_repo():
    """Test flattening a GitHub repository."""
    print("\n" + "=" * 60)
    print("TESTING GITHUB REPOSITORY FLATTENING")
    print("=" * 60)

    github_url = "https://github.com/acesanderson/Chain"
    print(f"Target: {github_url}")
    print()

    try:
        result = flatten_github_repo(github_url)

        # Basic validation
        if not result:
            print("❌ ERROR: No output generated")
            return False

        if not result.startswith("<?xml"):
            print("❌ ERROR: Output doesn't appear to be XML")
            return False

        if "<project name=" not in result:
            print("❌ ERROR: Missing project element")
            return False

        if "<directory_tree>" not in result:
            print("❌ ERROR: Missing directory_tree element")
            return False

        if "<file_contents>" not in result:
            print("❌ ERROR: Missing file_contents element")
            return False

        print("✅ SUCCESS: GitHub repository flattening completed")
        print(f"📊 Output length: {len(result)} characters")

        # Count some elements for validation
        file_count = result.count("<file ")
        cdata_count = result.count("<![CDATA[")
        print(f"📁 Files found: {file_count}")
        print(f"📄 CDATA sections: {cdata_count}")

        # Show a snippet of the output
        print("\n--- SAMPLE OUTPUT (first 500 chars) ---")
        print(result[:500] + "..." if len(result) > 500 else result)
        print("--- END SAMPLE ---")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False


def main():
    """Run all tests and report results."""
    print("🧪 FLATTEN TOOL TEST SUITE")
    print("Testing both local directory and GitHub repository functionality")

    results = []

    # Test local directory functionality
    results.append(("Local Directory", test_local_directory()))

    # Test GitHub repository functionality
    results.append(("GitHub Repository", test_github_repo()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The Flatten tool is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
