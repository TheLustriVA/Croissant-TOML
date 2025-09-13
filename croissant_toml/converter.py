"""
Croissant TOML/JSON-LD Converter.

Defines CLI-invokable functions for bidirectional conversion between Croissant
JSON-LD and TOML dataset metadata, including round-trip data integrity checks.
Handles parsing, normalization, TOML generation, rehydration to JSON-LD, and
utility routines for safe conversion workflows.
"""

import json
import tempfile
from pathlib import Path
from typing import Any

from .generator import generate_toml_from_dict
from .parser import parse_jsonld_to_dict
from .validator import toml_to_dict


def jsonld_to_toml(input_file: str, output_file: str) -> None:
    """Convert JSON-LD file to TOML format."""
    try:
        # Parse JSON-LD to dictionary
        data = parse_jsonld_to_dict(input_file)

        # Generate TOML from dictionary
        generate_toml_from_dict(data, output_file)

        print(f"Successfully converted {input_file} to {output_file}")

    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}") from e


def toml_to_jsonld(input_file: str, output_file: str) -> None:
    """Convert TOML file to JSON-LD format."""
    try:
        # Load TOML data
        data = toml_to_dict(input_file)

        # Convert back to JSON-LD structure
        jsonld_data = _toml_dict_to_jsonld(data)

        # Write to JSON-LD file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(jsonld_data, f, indent=2, ensure_ascii=False)

        print(f"Successfully converted {input_file} to {output_file}")

    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}") from e


def _toml_dict_to_jsonld(data: dict[str, Any]) -> dict[str, Any]:
    """Convert TOML dictionary structure back to JSON-LD format."""
    jsonld: dict[str, Any] = {
        "@context": {
            "sc": "https://schema.org/",
            "cr": "http://mlcommons.org/croissant/",
        }
    }

    # Handle metadata section
    if "metadata" in data:
        metadata = data["metadata"]

        # Basic metadata fields
        for key, value in metadata.items():
            if key == "schema":
                # Handle schema.org fields
                for schema_key, schema_value in value.items():
                    jsonld[f"sc:{schema_key}"] = schema_value
            elif key in ["conformsTo", "changeLog"]:
                # Keep these as-is
                jsonld[key] = value
            else:
                # Add schema.org prefix for common fields
                if key in [
                    "dateCreated",
                    "dateModified",
                    "datePublished",
                    "name",
                    "description",
                    "url",
                    "license",
                    "creator",
                    "version",
                    "keywords",
                ]:
                    jsonld[f"sc:{key}"] = value
                else:
                    jsonld[key] = value

    # Handle distribution section
    if "distribution" in data:
        jsonld["distribution"] = data["distribution"]

    # Handle recordsets section
    if "recordsets" in data:
        recordsets = []
        for _, recordset_data in data["recordsets"].items():
            recordset = {"@type": "cr:RecordSet"}
            recordset.update(recordset_data)
            recordsets.append(recordset)
        jsonld["cr:recordSet"] = recordsets

    # Handle RAI section
    if "rai" in data:
        # Add RAI fields with appropriate prefixes
        for key, value in data["rai"].items():
            jsonld[f"cr:{key}"] = value

    return jsonld


def validate_roundtrip(input_file: str) -> bool:
    """Validate that conversion roundtrip preserves data integrity."""
    try:
        # Use secure temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as temp_toml_file:
            temp_toml = temp_toml_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_jsonld_file:
            temp_jsonld = temp_jsonld_file.name

        try:
            # Convert to TOML and back
            jsonld_to_toml(input_file, temp_toml)
            toml_to_jsonld(temp_toml, temp_jsonld)

            # Load original and roundtrip data
            with open(input_file, encoding="utf-8") as f:
                original = json.load(f)

            with open(temp_jsonld, encoding="utf-8") as f:
                roundtrip = json.load(f)

            # Basic comparison (can be enhanced)
            return _compare_structures(original, roundtrip)

        finally:
            # Clean up temporary files
            Path(temp_toml).unlink(missing_ok=True)
            Path(temp_jsonld).unlink(missing_ok=True)

    except Exception as e:
        print(f"Roundtrip validation failed: {e}")
        return False


def _compare_structures(original: dict[str, Any], roundtrip: dict[str, Any]) -> bool:
    """Compare two dictionary structures for equivalence."""
    # This is a simplified comparison - can be enhanced for more thorough validation

    # Check if both have same set of keys (excluding context)
    orig_keys = {k for k in original.keys() if not k.startswith("@")}
    rt_keys = {k for k in roundtrip.keys() if not k.startswith("@")}

    if orig_keys != rt_keys:
        return False

    # Check basic field preservation
    for key in orig_keys:
        if key in ["name", "description", "version"]:
            orig_val = original.get(key) or original.get(f"sc: {key}")
            rt_val = roundtrip.get(key) or roundtrip.get(f"sc: {key}")
            if orig_val != rt_val:
                return False

    return True
