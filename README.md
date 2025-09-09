# Croissant TOML Converter

![banner of a croissant and the word TOML in front a blue abstract background with water reflecting underneath](https://i.imgur.com/8v647gr.jpg)

A Python tool for converting between [Croissant/Croissant-RAI](https://github.com/mlcommons/croissant) JSON-LD metadata and human-readable TOML format.

## Overview

This library provides bidirectional conversion between Croissant dataset metadata formats:

- **JSON-LD**: Machine-readable format following schema.org vocabulary
- **TOML**: Human-readable configuration format with comments and structure

## Rationale

TOML provides a far more accessible and genuinely open way of handling ML metadata than JSON-LD because of its human readability.

The effort put into acknowledging bias, potential harm, and the unintentional reenforcement of existing power structures in modern ML metadata seems, to me, utterly wasted if that very documentation can't be easily read by non-technical people.

I will be adding more tooling and specifications here as I make them.

I'm proud of the progress we as a discipline have made in ethical AI and I look forward to the industry itself catching up.

For more of my work on ethical AI and documentation, start here: [The Pile Datasheet](https://arxiv.org/abs/2201.07311)

## Features

- ✅ **Bidirectional conversion**: JSON-LD ↔ TOML
- ✅ **Context expansion**: Handles JSON-LD @context and prefixes  
- ✅ **Schema validation**: Validates TOML against Croissant schema
- ✅ **CLI interface**: Simple command-line tools
- ✅ **Human-friendly**: TOML output with comments and logical structure

## Installation

```bash
pip install -r requirements.txt
```

## CLI Usage

### Convert JSON-LD to TOML

```bash
python -m croissant_toml.cli to-toml dataset.json -o dataset.toml
```

### Convert TOML to JSON-LD

```bash
python -m croissant_toml.cli to-json dataset.toml -o dataset.json
```

### Validate TOML

```bash
python -m croissant_toml.cli validate dataset.toml
```

## TOML Schema Conventions

### Structure

The TOML format organizes Croissant metadata into three main sections:

```toml
[metadata]
name = "Dataset Name"
description = "Dataset description"
version = "1.0.0"
url = "https://example.com/dataset"
license = "MIT"
creator = "Author Name"
date_created = "2024-01-01"
date_modified = "2024-01-15"

[[record_sets]]
name = "examples"
description = "Example records"

[[record_sets.field]]
name = "text"
description = "Text content"
dataType = "sc:Text"

[[distributions]]
name = "data.csv"
contentUrl = "https://example.com/data.csv"
encodingFormat = "text/csv"
sha256 = "abc123..."
```

### Field Mappings

| JSON-LD | TOML | Description |
|---------|------|-------------|
| `name` | `metadata.name` | Dataset name |
| `description` | `metadata.description` | Dataset description |
| `dateCreated` | `metadata.date_created` | Creation date |
| `dateModified` | `metadata.date_modified` | Modification date |
| `cr:recordSet` | `record_sets` | Array of record sets |
| `distribution` | `distributions` | Array of file distributions |

## Programmatic Usage

### Basic Conversion

```python
from croissant_toml.converter import jsonld_to_toml, toml_to_jsonld

# JSON-LD to TOML
jsonld_to_toml('input.json', 'output.toml')

# TOML to JSON-LD  
toml_to_jsonld('input.toml', 'output.json')
```

### Validation

```python
from croissant_toml.validator import validate_toml_file

is_valid, errors = validate_toml_file('dataset.toml')
if not is_valid:
    print(f"Validation errors: {errors}")
```

### Custom Processing

```python
from croissant_toml.parser import parse_jsonld_to_dict
from croissant_toml.generator import generate_toml_from_dict

# Parse JSON-LD to normalized dict
data = parse_jsonld_to_dict('input.json')

# Modify data as needed
data['metadata']['custom_field'] = 'custom_value'

# Generate TOML
generate_toml_from_dict(data, 'output.toml')
```

## Extending for New Croissant Fields

To add support for new Croissant fields:

### 1. Update Schema

Edit `croissant_toml/schema.json` to include new field definitions:

```json
{
  "properties": {
    "metadata": {
      "properties": {
        "new_field": {
          "type": "string",
          "description": "Description of new field"
        }
      }
    }
  }
}
```

### 2. Update Parser

Add field mapping in `croissant_toml/parser.py`:

```python
field_mappings = {
    # ... existing mappings
    'newJsonLdKey': 'metadata.new_field'
}
```

### 3. Update Generator  

Add field to ordering and comments in `croissant_toml/generator.py`:

```python
field_order = [
    # ... existing fields
    'new_field'
]
```

### 4. Update Converter

Add reverse mapping in `croissant_toml/converter.py`:

```python
field_mappings = {
    # ... existing mappings
    'new_field': 'newJsonLdKey'
}
```

## Project Structure

```bash
croissant_toml/
├── __init__.py         # Package initialization
├── cli.py              # Command-line interface
├── parser.py           # JSON-LD parsing and normalization
├── generator.py        # TOML generation with comments
├── validator.py        # TOML validation against schema
├── converter.py        # High-level conversion orchestration
├── schema.json         # JSON Schema for TOML validation
└── README.md           # Documentation
```

## Development

### Running Tests

```bash
# Validate sample conversion
python -m croissant_toml.cli to-toml sample.json
python -m croissant_toml.cli validate sample.toml
python -m croissant_toml.cli to-json sample.toml -o roundtrip.json
```

### Adding New Features

1. Update the appropriate module (`parser.py`, `generator.py`, etc.)
2. Update `schema.json` if adding new fields
3. Update field mappings in `converter.py`
4. Test conversion roundtrips

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Limitations

- Complex JSON-LD structures may require manual adjustment
- Some semantic information may be lost in conversion
- TOML format limitations (no null values, limited nesting)

## Future Enhancements

- [ ] Support for more Croissant-RAI fields
- [ ] Configurable TOML formatting options  
- [ ] Better error reporting and recovery
- [ ] Integration with Croissant validation tools
- [ ] Support for JSON-LD frames and compaction
