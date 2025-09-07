#!/usr/bin/env python3
"""
Test script to verify the Croissant TOML converter MVP.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from croissant_toml.converter import jsonld_to_toml, toml_to_jsonld
from croissant_toml.validator import validate_toml_file


def test_conversion():
    """Test JSON-LD to TOML conversion."""
    print("Testing JSON-LD to TOML conversion...")
    
    try:
        # Convert sample JSON-LD to TOML
        jsonld_to_toml("sample.json", "sample.toml")
        print("✓ JSON-LD to TOML conversion successful")
        
        # Validate generated TOML
        is_valid, errors = validate_toml_file("sample.toml")
        if is_valid:
            print("✓ Generated TOML is valid")
        else:
            print(f"✗ TOML validation failed: {errors}")
            return False
        
        # Convert back to JSON-LD
        toml_to_jsonld("sample.toml", "sample_roundtrip.json")
        print("✓ TOML to JSON-LD conversion successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        return False


def test_cli():
    """Test CLI interface."""
    print("\nTesting CLI interface...")
    
    try:
        import subprocess
        
        # Test to-toml command
        result = subprocess.run([
            sys.executable, "-m", "croissant_toml.cli", 
            "to-toml", "sample.json", "-o", "cli_sample.toml"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ CLI to-toml command successful")
        else:
            print(f"✗ CLI to-toml failed: {result.stderr}")
            return False
        
        # Test validate command
        result = subprocess.run([
            sys.executable, "-m", "croissant_toml.cli", 
            "validate", "cli_sample.toml"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ CLI validate command successful")
        else:
            print(f"✗ CLI validate failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Croissant TOML Converter MVP Test")
    print("=" * 40)
    
    success = True
    
    # Test conversions
    success &= test_conversion()
    
    # Test CLI
    success &= test_cli()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! MVP is working correctly.")
        
        # Display sample TOML output
        if os.path.exists("sample.toml"):
            print("\nGenerated TOML preview:")
            print("-" * 30)
            with open("sample.toml", "r") as f:
                preview = f.read()[:500]
                print(preview)
                if len(f.read()) > 500:
                    print("... (truncated)")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
