"""
Croissant JSON-LD Parser and Normalizer.

Parses and normalizes Croissant-compliant JSON-LD metadata files into
dictionary structures ready for TOML serialization. Handles key flattening,
schema.org field grouping, controlled vocabulary mapping, and backward
compatibility for Croissant metadata variants.
"""

import json
import re
from typing import Any

# Silence specific security warning for RDF parsing  # nosec


def parse_jsonld_to_dict(jsonld_file_path: str) -> dict[str, Any]:
    """Parse JSON-LD file and return normalized dictionary with flattened keys."""
    with open(jsonld_file_path, encoding="utf-8") as f:
        jsonld_data = json.load(f)

    # Optional RDF validation - skip if rdflib not available
    try:
        from rdflib import Graph

        graph = Graph()
        graph.parse(data=json.dumps(jsonld_data), format="json-ld")
    except ImportError:
        # Continue without RDF validation if rdflib not available
        pass
    except Exception:  # nosec - Intentionally broad exception handling for optional RDF
        # Continue without RDF validation if parsing fails
        pass

    # Extract normalized data structure directly from JSON-LD
    normalized_data: dict[str, Any] = {}

    if isinstance(jsonld_data, dict):
        # Extract @context
        context = jsonld_data.get("@context", {})

        # Flatten and normalize keys
        flattened = _flatten_jsonld_keys(jsonld_data, context)
        normalized_data = _normalize_croissant_structure(flattened)

    return normalized_data


def _flatten_jsonld_keys(
    data: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Flatten JSON-LD keys by removing prefixes and expanding contexts."""
    flattened: dict[str, Any] = {}

    for key, value in data.items():
        if key.startswith("@"):
            continue

        # Remove common prefixes like cr: and sc:
        clean_key = key
        if ":" in key:
            clean_key = key.split(":", 1)[1]

        # Handle nested structures
        if isinstance(value, dict):
            flattened[clean_key] = _flatten_jsonld_keys(value, context)
        elif isinstance(value, list):
            flattened[clean_key] = [
                (
                    _flatten_jsonld_keys(item, context)
                    if isinstance(item, dict)
                    else item
                )
                for item in value
            ]
        else:
            flattened[clean_key] = value

    return flattened


def _normalize_croissant_structure(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize Croissant-specific structure for TOML conversion."""
    normalized: dict[str, Any] = {
        "metadata": {},
        "recordsets": {},  # Changed from record_sets to match spec
        "distribution": [],  # Changed to match spec (array of tables)
    }

    # Map common Croissant fields with proper camelCase preservation
    field_mappings = {
        "name": "metadata.name",
        "description": "metadata.description",
        "version": "metadata.version",
        "url": "metadata.url",
        "license": "metadata.license",
        "creator": "metadata.creator",
        "conformsTo": "metadata.conformsTo",  # Required field from spec
        "changeLog": "metadata.changeLog",  # Version management from spec
        # Preserve camelCase for schema.org fields
        "dateCreated": "metadata.dateCreated",
        "dateModified": "metadata.dateModified",
        "datePublished": "metadata.datePublished",
        "recordSet": "recordsets",
        "distribution": "distribution",
    }

    # Handle RAI section
    if "rai" in data or any(key.startswith("rai") for key in data.keys()):
        normalized["rai"] = {}

    for key, value in data.items():
        if key in field_mappings:
            target_path = field_mappings[key]
            _set_nested_value(normalized, target_path, value)
        elif _is_schema_org_field(key):
            # Group schema.org fields under metadata.schema
            if "schema" not in normalized["metadata"]:
                normalized["metadata"]["schema"] = {}
            normalized["metadata"]["schema"][key] = value
        elif key.startswith("rai") or key == "rai":
            # Handle RAI fields
            if key == "rai":
                normalized["rai"] = value
            else:
                # Handle rai.* fields
                rai_key = key[4:] if key.startswith("rai.") else key
                normalized["rai"][rai_key] = value
        else:
            # Handle unknown fields in metadata section
            normalized["metadata"][key] = value

    # Handle backward compatibility - recognize both naming conventions
    if "record_sets" in data:
        normalized["recordsets"] = data["record_sets"]
    if "distributions" in data and isinstance(data["distributions"], list):
        normalized["distribution"] = data["distributions"]

    return normalized


def _is_schema_org_field(key: str) -> bool:
    """Check if a field belongs to schema.org vocabulary."""
    # Common schema.org fields that should be preserved in camelCase
    schema_org_fields = {
        "author",
        "contributor",
        "copyrightHolder",
        "copyrightYear",
        "dateCreated",
        "dateModified",
        "datePublished",
        "encodingFormat",
        "contentSize",
        "contentUrl",
        "downloadUrl",
        "fileFormat",
        "keywords",
        "mainEntity",
        "publisher",
        "spatialCoverage",
        "temporalCoverage",
        "variableMeasured",
        "isAccessibleForFree",
    }

    return key in schema_org_fields or key.startswith(("sc:", "schema:"))


def _set_nested_value(data: dict[str, Any], path: str, value: Any) -> None:
    """Set value at nested path in dictionary."""
    parts = path.split(".")
    current = data

    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value


def normalize_field_names_for_toml(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize field names for TOML while preserving camelCase where appropriate."""
    normalized: dict[str, Any] = {}
    for key, value in data.items():
        # Preserve camelCase for schema.org fields
        if _is_schema_org_field(key):
            normalized[key] = normalize_field_names_for_toml(value)
        else:
            # Convert to snake_case for internal fields if needed
            normalized_key = (
                _to_snake_case(key) if not _is_schema_org_field(key) else key
            )
            normalized[normalized_key] = normalize_field_names_for_toml(value)
    return normalized


def _to_snake_case(name: str) -> str:
    """Convert camelCase to snake_case for internal fields."""
    # Insert underscore before uppercase letters that follow lowercase letters
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # Insert underscore before uppercase letters that follow lowercase letters or digits
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
