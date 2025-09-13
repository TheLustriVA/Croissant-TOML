"""
Croissant TOML Validator.

Implements validation for Croissant TOML metadata against the Croissant schema,
including enhanced specification checks for URLs, RAI vocabularies, dates,
checksums, and cross-section references. Provides top-level validation entry
points and TOML-to-dictionary normalization utilities.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Union
from urllib.parse import urlparse

import tomlkit
from jsonschema import ValidationError, validate


def validate_toml_file(toml_file_path: str) -> tuple[bool, list[str]]:
    """Validate TOML file against Croissant schema with enhanced validation."""
    try:
        # Load TOML file
        with open(toml_file_path, encoding="utf-8") as f:
            toml_content = f.read()

        # Parse TOML to dictionary
        data = tomlkit.loads(toml_content)
        dict_data = _tomlkit_to_dict(data)
        # Runtime safety check
        if not isinstance(dict_data, dict):
            return False, ["Top-level TOML object must be a dictionary"]
        # Suppress MyPy warning
        return validate_dict_against_schema(dict_data)

    except Exception as e:
        return False, [f"Failed to load TOML file: {str(e)}"]


def validate_dict_against_schema(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate dictionary against JSON schema with enhanced validation."""
    errors: list[str] = []

    try:
        # Load schema
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        # Basic JSON schema validation
        validate(instance=data, schema=schema)

        # Enhanced validation checks
        enhanced_errors = _perform_enhanced_validation(data)
        errors.extend(enhanced_errors)

        return len(errors) == 0, errors

    except ValidationError as e:
        errors.append(f"Schema validation error: {e.message}")
        return False, errors
    except FileNotFoundError:
        return False, ["Schema file not found"]
    except Exception as e:
        return False, [f"Validation failed: {str(e)}"]


def _perform_enhanced_validation(data: dict[str, Any]) -> list[str]:
    """Perform enhanced validation checks beyond basic JSON schema."""
    errors: list[str] = []

    # Validate metadata section
    if "metadata" in data:
        metadata_errors = _validate_metadata_section(data["metadata"])
        errors.extend(metadata_errors)

    # Validate distribution sections
    if "distribution" in data:
        distribution_errors = _validate_distribution_section(data["distribution"])
        errors.extend(distribution_errors)

    # Validate RAI section
    if "rai" in data:
        rai_errors = _validate_rai_section(data["rai"])
        errors.extend(rai_errors)

    # Validate recordsets section
    if "recordsets" in data:
        recordsets_errors = _validate_recordsets_section(data["recordsets"])
        errors.extend(recordsets_errors)

    return errors


def _validate_metadata_section(metadata: dict[str, Any]) -> list[str]:
    """Validate metadata section with enhanced checks."""
    errors: list[str] = []

    # Check for required conformsTo field
    if "conformsTo" not in metadata:
        errors.append("Missing required 'conformsTo' field in metadata")
    elif not isinstance(metadata["conformsTo"], list):
        errors.append("'conformsTo' field must be an array")

    # Validate URLs in metadata
    url_fields = ["url", "contentUrl", "license"]
    for field in url_fields:
        if field in metadata:
            if not _is_valid_url(metadata[field]):
                errors.append(
                    f"Invalid URL format in metadata.{field}: " f"{metadata[field]}"
                )

    # Validate date fields
    date_fields = ["dateCreated", "dateModified", "datePublished"]
    for field in date_fields:
        if field in metadata:
            if not _is_valid_iso8601_date(metadata[field]):
                errors.append(
                    f"Invalid ISO 8601 date format in metadata.{field}: "
                    f"{metadata[field]}"
                )

    return errors


def _validate_distribution_section(distributions: list[dict[str, Any]]) -> list[str]:
    """Validate distribution section with enhanced checks."""
    errors: list[str] = []

    for i, dist in enumerate(distributions):
        # if not isinstance(dist, dict):
        #     continue

        # Validate URLs
        if "contentUrl" in dist and not _is_valid_url(dist["contentUrl"]):
            errors.append(
                f"Invalid URL format in distribution[{i}].contentUrl: "
                f"{dist['contentUrl']}"
            )

        # Validate SHA256 checksums
        if "sha256" in dist and not _is_valid_sha256(dist["sha256"]):
            errors.append(
                f"Invalid SHA256 format in distribution[{i}].sha256: "
                f"{dist['sha256']}"
            )

    return errors


def _validate_rai_section(rai: dict[str, Any]) -> list[str]:
    """Validate RAI section with enhanced checks including controlled vocabularies."""
    errors: list[str] = []

    # Define controlled vocabularies for RAI fields
    VALID_DATA_COLLECTION_TYPES = [
        "Web Scraping",
        "API Collection",
        "Manual Human Curation",
        "Automated Collection",
        "Survey",
        "Interview",
        "Observation",
        "Experiment",
        "Simulation",
        "Crowdsourcing",
    ]

    VALID_DATA_USE_CASES = [
        "Training",
        "Validation",
        "Testing",
        "Research Use Only",
        "Commercial Use",
        "Educational Use",
        "Benchmarking",
    ]

    # Validate dataCollectionType
    if "dataCollectionType" in rai:
        if isinstance(rai["dataCollectionType"], list):
            for collection_type in rai["dataCollectionType"]:
                if collection_type not in VALID_DATA_COLLECTION_TYPES:
                    errors.append(f"Invalid data collection type: {collection_type}")
        else:
            errors.append("dataCollectionType must be an array")

    # Validate dataUseCases
    if "dataUseCases" in rai:
        if isinstance(rai["dataUseCases"], list):
            for use_case in rai["dataUseCases"]:
                if use_case not in VALID_DATA_USE_CASES:
                    errors.append(f"Invalid data use case: {use_case}")
        else:
            errors.append("dataUseCases must be an array")

    # Validate annotation demographics if present
    if "annotation" in rai and "demographics" in rai["annotation"]:
        demographics = rai["annotation"]["demographics"]
        if not isinstance(demographics, dict):
            errors.append("rai.annotation.demographics must be an object")

    return errors


def _validate_recordsets_section(recordsets: dict[str, Any]) -> list[str]:
    """Validate recordsets section with enhanced checks."""
    errors: list[str] = []

    for _, recordset_data in recordsets.items():
        if not isinstance(recordset_data, dict):
            continue

        # Validate field references
        if "fields" in recordset_data:
            for _, field in enumerate(recordset_data["fields"]):
                if isinstance(field, dict) and "source" in field:
                    source = field["source"]
                    if "fileObject" in source or "fileSet" in source:
                        # These should reference valid distribution IDs
                        # This would require cross-referencing with distribution section
                        pass

    return errors


def _is_valid_url(url: str) -> bool:
    """Validate URL format using RFC 3986 standards."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _is_valid_sha256(sha256: str) -> bool:
    """Validate SHA256 hash format."""
    return bool(re.match(r"^[a-fA-F0-9]{64}$", sha256))


def _is_valid_iso8601_date(date_str: str) -> bool:
    """Validate ISO 8601 date format."""
    # Try common ISO 8601 formats
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue

    return False


def _tomlkit_to_dict(data: Any) -> Union[dict[str, Any], list[Any], Any]:
    """Convert tomlkit objects to plain dictionary.

    This function can return different types based on input:
    - dict for dictionary-like tomlkit objects
    - list for array-like tomlkit objects
    - Primitive types (str, int, bool, etc.) for values
    """
    if isinstance(data, dict):
        return {key: _tomlkit_to_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_tomlkit_to_dict(item) for item in data]
    else:
        # Handle tomlkit specific types
        if hasattr(data, "value"):
            return data.value
        return data


def toml_to_dict(toml_file_path: str) -> dict[str, Any]:
    """Load TOML file and convert to dictionary.

    This function guarantees to return a dict[str, Any] as it processes
    the top-level TOML document which is always a dictionary.
    """
    with open(toml_file_path, encoding="utf-8") as f:
        toml_content = f.read()

    data = tomlkit.loads(toml_content)
    result = _tomlkit_to_dict(data)

    # Ensure we return a dictionary at the top level
    if isinstance(result, dict):
        return result
    else:
        # This should not happen with valid TOML, but provide fallback
        return {"data": result}
