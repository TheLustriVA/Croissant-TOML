import json
from pathlib import Path
from typing import Dict, Any
import tomlkit


def generate_toml_from_dict(data: Dict[str, Any], output_path: str):
    """Generate human-friendly TOML from normalized dictionary."""

    # Load schema for field descriptions
    schema_path = Path(__file__).parent / 'schema.json'
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    doc = tomlkit.document()

    # Add header comment
    doc.add(tomlkit.comment("Croissant Dataset Metadata"))
    doc.add(tomlkit.comment("Generated from JSON-LD format"))
    doc.add(tomlkit.nl())

    # Add metadata section
    if 'metadata' in data and data['metadata']:
        doc.add("metadata", _build_metadata_section(data['metadata'], schema))

    # Add record sets section
    if 'record_sets' in data and data['record_sets']:
        doc.add(tomlkit.nl())
        doc.add("record_sets", _build_record_sets_section(data['record_sets'], schema))

    # Add distributions section
    if 'distributions' in data and data['distributions']:
        doc.add(tomlkit.nl())
        doc.add("distributions", _build_distributions_section(data['distributions'], schema))

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tomlkit.dumps(doc))


def _build_metadata_section(metadata: Dict[str, Any], schema: Dict[str, Any]) -> tomlkit.Table:
    """Build metadata section with comments."""
    table = tomlkit.table()

    # Core metadata fields with comments
    field_order = ['name', 'description', 'version', 'url', 'license', 'creator', 'date_created', 'date_modified']

    for field in field_order:
        if field in metadata:
            # Add field comment if available in schema
            field_desc = schema.get('properties', {}).get('metadata', {}).get('properties', {}).get(field, {}).get('description')
            if field_desc:
                table.add(tomlkit.comment(f"{field_desc}"))

            table.add(field, metadata[field])
            table.add(tomlkit.nl())

    # Add remaining fields
    for key, value in metadata.items():
        if key not in field_order:
            table.add(key, value)

    return table


def _build_record_sets_section(record_sets: list, schema: Dict[str, Any]) -> tomlkit.Array:
    """Build record sets section."""
    array = tomlkit.array()

    for record_set in record_sets:
        if isinstance(record_set, dict):
            rs_table = tomlkit.table()

            # Add common record set fields
            for key, value in record_set.items():
                rs_table.add(key, value)

            array.append(rs_table)
        else:
            array.append(record_set)

    return array


def _build_distributions_section(distributions: list, schema: Dict[str, Any]) -> tomlkit.Array:
    """Build distributions section."""
    array = tomlkit.array()

    for distribution in distributions:
        if isinstance(distribution, dict):
            dist_table = tomlkit.table()

            # Add common distribution fields
            for key, value in distribution.items():
                dist_table.add(key, value)

            array.append(dist_table)
        else:
            array.append(distribution)

    return array


def dict_to_toml_string(data: Dict[str, Any]) -> str:
    """Convert dictionary to TOML string."""
    doc = tomlkit.document()

    for key, value in data.items():
        doc.add(key, value)

    return tomlkit.dumps(doc)
