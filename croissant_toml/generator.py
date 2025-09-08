import json
from pathlib import Path
from typing import Dict, Any
import tomlkit


def generate_toml_from_dict(data: Dict[str, Any], output_path: str):
    """Generate human-friendly TOML from normalized dictionary."""

    # Load schema for field descriptions
    try:
        schema_path = Path(__file__).parent / 'schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)
    except FileNotFoundError:
        schema = {}  # Fallback if schema not found

    doc = tomlkit.document()

    # Add header comment
    doc.add(tomlkit.comment("Croissant Dataset Metadata"))
    doc.add(tomlkit.comment("Generated from JSON-LD format"))
    doc.add(tomlkit.nl())

    # Add metadata section as a table
    if 'metadata' in data and data['metadata']:
        metadata_table = _build_metadata_table(data['metadata'], schema)
        doc.add("metadata", metadata_table)
        doc.add(tomlkit.nl())

    # Add record sets as Array of Tables (AOT)
    if 'record_sets' in data and data['record_sets']:
        _add_record_sets_aot(doc, data['record_sets'], schema)
        doc.add(tomlkit.nl())

    # Add distributions as Array of Tables (AOT)
    if 'distributions' in data and data['distributions']:
        _add_distributions_aot(doc, data['distributions'], schema)

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tomlkit.dumps(doc))


def _build_metadata_table(metadata: Dict[str, Any], schema: Dict[str, Any]) -> tomlkit.table:
    """Build metadata section as a proper TOML table."""
    table = tomlkit.table()

    # Core metadata fields in logical order
    field_order = ['name', 'description', 'version', 'url', 'license', 'creator', 'date_created', 'date_modified']

    # Add fields in order
    for field in field_order:
        if field in metadata:
            _add_field_with_comment(table, field, metadata[field], schema)

    # Add remaining fields
    for key, value in metadata.items():
        if key not in field_order:
            table.add(key, value)

    return table


def _add_field_with_comment(table: tomlkit.table, field: str, value: Any, schema: Dict[str, Any]):
    """Add field to table with optional comment from schema."""
    # Try to get field description from schema
    try:
        field_desc = schema.get('properties', {}).get('metadata', {}).get('properties', {}).get(field, {}).get('description')
        if field_desc:
            table.add(tomlkit.comment(field_desc))
    except ValueError:
        pass

    table.add(field, value)


def _add_record_sets_aot(doc: tomlkit.document, record_sets: list, schema: Dict[str, Any]):
    """Add record sets as Array of Tables."""

    for record_set in record_sets:
        if not isinstance(record_set, dict):
            continue

        # Create table for this record set
        rs_table = tomlkit.table()

        # Add basic record set fields
        basic_fields = ['name', 'description', '@type']
        for field in basic_fields:
            if field in record_set:
                rs_table.add(field, record_set[field])

        # Handle fields array within record set
        if 'field' in record_set and isinstance(record_set['field'], list):
            for field in record_set['field']:
                if isinstance(field, dict):
                    field_table = tomlkit.table()

                    # Add all field properties
                    for key, value in field.items():
                        field_table.add(key, value)

                    # Add to record set as nested Array of Tables
                    if "field" not in rs_table:
                        rs_table.add("field", tomlkit.aot())
                    rs_table["field"].append(field_table)

        # Add other record set properties
        for key, value in record_set.items():
            if key not in basic_fields + ['field']:
                rs_table.add(key, value)

        # Add record set to document as Array of Tables
        if "record_sets" not in doc:
            doc.add("record_sets", tomlkit.aot())
        doc["record_sets"].append(rs_table)


def _add_distributions_aot(doc: tomlkit.document, distributions: list, schema: Dict[str, Any]):
    """Add distributions as Array of Tables."""

    for distribution in distributions:
        if not isinstance(distribution, dict):
            continue

        # Create table for this distribution
        dist_table = tomlkit.table()

        # Add all distribution properties
        for key, value in distribution.items():
            dist_table.add(key, value)

        # Add distribution to document as Array of Tables
        if "distributions" not in doc:
            doc.add("distributions", tomlkit.aot())
        doc["distributions"].append(dist_table)


def dict_to_toml_string(data: Dict[str, Any]) -> str:
    """Convert dictionary to TOML string."""
    doc = tomlkit.document()

    # Handle metadata as table
    if 'metadata' in data:
        doc.add('metadata', data['metadata'])

    # Handle arrays as Array of Tables
    for key, value in data.items():
        if key == 'metadata':
            continue
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            # Array of objects -> Array of Tables
            aot = tomlkit.aot()
            for item in value:
                if isinstance(item, dict):
                    table = tomlkit.table()
                    for k, v in item.items():
                        table.add(k, v)
                    aot.append(table)
            doc.add(key, aot)
        else:
            doc.add(key, value)

    return tomlkit.dumps(doc)
