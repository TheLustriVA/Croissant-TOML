"""
Generator Functions for Croissant TOML Output.

Defines routines for generating human-readable TOML dataset metadata from a
normalized Croissant dictionary structure. Handles TOMLKit document/table
generation, field ordering, field descriptions, array-of-tables, nested
recordset construction, and specification-compliant rendering.
"""

import json
from pathlib import Path
from typing import Any, Optional, cast

import tomlkit
from tomlkit import table


def generate_toml_from_dict(data: dict[str, Any], output_path: str) -> None:
    """Generate human-friendly TOML from normalized dictionary."""
    # Load schema for field descriptions
    try:
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
    except FileNotFoundError:
        schema = {}  # Fallback if schema not found

    doc = tomlkit.document()

    # Add header comment
    doc.add(tomlkit.comment("Croissant Dataset Metadata"))
    doc.add(tomlkit.comment("Generated from JSON-LD format"))
    doc.add(tomlkit.comment("Conforms to: http://mlcommons.org/croissant/1.0"))
    doc.add(tomlkit.nl())

    # Add metadata section as a table
    if "metadata" in data and data["metadata"]:
        metadata_table = _build_metadata_table(data["metadata"], schema)
        doc.add("metadata", metadata_table)
        doc.add(tomlkit.nl())

    # Add distribution as Array of Tables (AOT) - spec uses [[distribution]]
    if "distribution" in data and data["distribution"]:
        _add_distribution_aot(doc, data["distribution"], schema)
        doc.add(tomlkit.nl())

    # Add recordsets as nested tables - spec uses [recordsets.name]
    if "recordsets" in data and data["recordsets"]:
        _add_recordsets_tables(doc, data["recordsets"], schema)
        doc.add(tomlkit.nl())

    # Add RAI section as a table - spec uses [rai]
    if "rai" in data and data["rai"]:
        _add_rai_table(doc, data["rai"], schema)

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))


def _build_metadata_table(
    metadata: dict[str, Any], schema: dict[str, Any]
) -> Any:  # Use Any for tomlkit.Table compatibility
    """Build metadata section as a proper TOML table with required fields."""
    metadata_table = tomlkit.table()

    # Core metadata fields in logical order based on spec
    field_order = [
        "conformsTo",  # Required field from spec
        "name",
        "description",
        "version",
        "url",
        "license",
        "datePublished",
        "dateCreated",
        "dateModified",  # Preserve camelCase
        "creator",
        "keywords",
        "changeLog",  # Version management
    ]

    # Add conformsTo if missing (default values from spec)
    if "conformsTo" not in metadata:
        metadata_table.add(tomlkit.comment("Required: Specification conformance"))
        metadata_table.add(
            "conformsTo",
            [
                "http://mlcommons.org/croissant/1.0",
                "http://mlcommons.org/croissant/RAI/1.0",
            ],
        )

    # Add fields in order with comments
    for field in field_order:
        if field in metadata:
            _add_field_with_comment(metadata_table, field, metadata[field], schema)

    # Handle schema.org fields in a nested table
    if "schema" in metadata:
        schema_table = tomlkit.table()
        for key, value in metadata["schema"].items():
            _add_field_with_comment(schema_table, key, value, schema)
        metadata_table.add("schema", schema_table)

    # Add remaining fields
    for key, value in metadata.items():
        if key not in field_order + ["schema"]:
            if _is_schema_org_field(key):
                # Add to schema section
                if "schema" not in metadata_table:
                    metadata_table.add("schema", tomlkit.table())
                schema_section = metadata_table["schema"]
                if hasattr(schema_section, "add"):
                    schema_section.add(key, value)
            else:
                metadata_table.add(key, value)

    return metadata_table


def _add_field_with_comment(
    table_for_comment: Any, field: str, value: Any, schema: dict[str, Any]
) -> None:
    """Add field to table with optional comment from schema or field description."""
    # Generate helpful comments based on field name and spec
    comment = _get_field_comment(field)

    if comment:
        table_for_comment.add(tomlkit.comment(comment))

    table_for_comment.add(field, value)


def _get_field_comment(field: str) -> Optional[str]:
    """Get descriptive comment for common fields based on specification."""
    comments = {
        "conformsTo": "Specification conformance URLs",
        "name": "Dataset name",
        "description": "Comprehensive dataset description",
        "license": "License URL or identifier",
        "url": "Dataset homepage URL",
        "datePublished": "Publication date in ISO 8601 format",
        "dateCreated": "Creation date in ISO 8601 format",
        "dateModified": "Last modification date in ISO 8601 format",
        "version": "Dataset version (semantic versioning recommended)",
        "keywords": "Dataset keywords/tags",
        "changeLog": "Version change history",
        "creator": "Dataset creator/organization information",
        "dataCollection": "Description of data collection process",
        "dataBiases": "Known biases in the dataset",
        "dataLimitations": "Dataset limitations and constraints",
        "dataUseCases": "Intended use cases for the dataset",
    }

    return comments.get(field)


def _add_distribution_aot(
    doc: Any, distributions: list[dict[str, Any]], schema: dict[str, Any]
) -> None:
    """Add distributions as Array of Tables following spec format [[distribution]]."""
    for distribution in distributions:
        # Create table for this distribution
        dist_table = tomlkit.table()

        # Add distribution properties in logical order
        property_order = [
            "type",
            "id",
            "name",
            "contentUrl",
            "encodingFormat",
            "sha256",
        ]

        for prop in property_order:
            if prop in distribution:
                _add_field_with_comment(dist_table, prop, distribution[prop], schema)

        # Add remaining properties
        for key, value in distribution.items():
            if key not in property_order:
                dist_table.add(key, value)

        # Add distribution to document as Array of Tables
        if "distribution" not in doc:
            doc.add("distribution", tomlkit.aot())

        doc_distribution = doc["distribution"]
        if hasattr(doc_distribution, "append"):
            doc_distribution.append(dist_table)


def _add_recordsets_tables(
    doc: Any, recordsets: dict[str, Any], schema: dict[str, Any]
) -> None:
    """Add recordsets as nested tables following spec format [recordsets.name]."""
    for recordset_name, recordset_data in recordsets.items():
        if not isinstance(recordset_data, dict):
            continue

        # Create the recordset table path
        recordset_path = f"recordsets.{recordset_name}"
        recordset_table = tomlkit.table()

        # Add basic recordset properties
        basic_fields = ["type", "id", "key", "description"]
        for field in basic_fields:
            if field in recordset_data:
                _add_field_with_comment(
                    recordset_table, field, recordset_data[field], schema
                )

        # Handle fields array as Array of Tables
        if "fields" in recordset_data and isinstance(recordset_data["fields"], list):
            for field in recordset_data["fields"]:
                if isinstance(field, dict):
                    field_table = tomlkit.table()

                    # Add field properties in logical order
                    field_order = ["id", "name", "dataType", "description"]
                    for prop in field_order:
                        if prop in field:
                            _add_field_with_comment(
                                field_table, prop, field[prop], schema
                            )

                    # Handle source information
                    if "source" in field:
                        source_table = tomlkit.table()
                        for key, value in field["source"].items():
                            source_table.add(key, value)
                        field_table.add("source", source_table)

                    # Add remaining field properties
                    for key, value in field.items():
                        if key not in field_order + ["source"]:
                            field_table.add(key, value)

                    # Add to recordset as Array of Tables
                    if "fields" not in recordset_table:
                        recordset_table.add("fields", tomlkit.aot())

                    recordset_fields = recordset_table["fields"]
                    if hasattr(recordset_fields, "append"):
                        recordset_fields.append(field_table)

        # Add other recordset properties
        for key, value in recordset_data.items():
            if key not in basic_fields + ["fields"]:
                recordset_table.add(key, value)

        # Add recordset table to document
        doc.add(recordset_path, recordset_table)


def _add_rai_table(doc: Any, rai_data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Add RAI section as table following spec format [rai]."""
    rai_table = tomlkit.table()

    # Add comment for RAI section
    doc.add(tomlkit.comment("Responsible AI metadata"))

    # RAI fields in logical order from spec
    rai_field_order = [
        "dataCollection",
        "dataCollectionType",
        "dataPreprocessingProtocol",
        "dataBiases",
        "dataLimitations",
        "dataUseCases",
        "personalSensitiveInformation",
    ]

    # Add RAI fields with comments
    for field in rai_field_order:
        if field in rai_data:
            _add_field_with_comment(rai_table, field, rai_data[field], schema)

    # Handle annotation subsection
    if "annotation" in rai_data:
        annotation_table = tomlkit.table()
        annotation_data = rai_data["annotation"]

        # Add annotation fields
        annotation_fields = [
            "annotationPlatform",
            "annotationsPerItem",
            "totalAnnotators",
        ]
        for field in annotation_fields:
            if field in annotation_data:
                annotation_table.add(field, annotation_data[field])

        # Handle demographics subsection
        if "demographics" in annotation_data:
            demographics_table = tomlkit.table()
            for key, value in annotation_data["demographics"].items():
                demographics_table.add(key, value)
            annotation_table.add("demographics", demographics_table)

        # Add remaining annotation fields
        for key, value in annotation_data.items():
            if key not in annotation_fields + ["demographics"]:
                annotation_table.add(key, value)

        rai_table.add("annotation", annotation_table)

    # Add remaining RAI fields
    for key, value in rai_data.items():
        if key not in rai_field_order + ["annotation"]:
            rai_table.add(key, value)

    # Add RAI table to document
    doc.add("rai", rai_table)


def _is_schema_org_field(key: str) -> bool:
    """Check if a field belongs to schema.org vocabulary."""
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


def dict_to_toml_string(data: dict[str, Any]) -> str:
    """Convert dictionary to TOML string with proper structure."""
    doc = tomlkit.document()

    # Handle metadata as table - PRESERVED ORIGINAL BEHAVIOR
    if "metadata" in data:
        doc.add("metadata", data["metadata"])  # Original automatic conversion

    # Handle arrays as Array of Tables
    for key, value in data.items():
        if key == "metadata":
            continue
        elif (
            key == "distribution"
            and isinstance(value, list)
            and value
            and isinstance(value[0], dict)
        ):
            # Array of objects -> Array of Tables
            aot = tomlkit.aot()
            for item in value:
                if isinstance(item, dict):
                    item_table = tomlkit.table()
                    for k, v in item.items():
                        item_table.add(k, v)
                    aot.append(table)
            doc.add(key, aot)
        elif key == "recordsets" and isinstance(value, dict):
            # Nested recordsets structure
            for recordset_name, recordset_data in value.items():
                if isinstance(recordset_data, dict):
                    recordset_table = table()
                    for k, v in recordset_data.items():
                        recordset_table.add(k, v)
                    doc.add(f"recordsets.{recordset_name}", recordset_table)
        else:
            doc.add(key, value)

    return cast(str, tomlkit.dumps(doc))
