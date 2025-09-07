# Croissant TOML Converter MVP

A complete Python MVP for converting between Croissant/Croissant-RAI JSON-LD metadata and human-readable TOML format.

## Project Structure

```
croissant_toml/
├── __init__.py         # Package initialization
├── cli.py              # CLI entrypoint using click
├── parser.py           # JSON-LD → normalized dict
├── generator.py        # dict → TOML via tomlkit
├── validator.py        # tomlkit → dict → jsonschema validation
├── converter.py        # round-trip JSON-LD ↔ TOML functions
├── schema.json         # JSON Schema mapping Croissant JSON-LD keys to TOML fields
└── README.md           # Documentation
requirements.txt        # Dependencies
setup.py               # Package installation
sample.json            # Sample Croissant JSON-LD file
test_mvp.py            # Test script
```

## Features Implemented

✅ **CLI Commands**:
- `to-toml <input.json> -o <output.toml>`
- `to-json <input.toml> -o <output.json>`  
- `validate <input.toml>`

✅ **Core Components**:
- `parser.py` - Uses `rdflib-jsonld` to expand contexts and flatten keys
- `generator.py` - Uses `tomlkit` to emit human-friendly, commented TOML
- `validator.py` - Validates TOML against JSON schema
- `converter.py` - Orchestrates round-trip conversions

✅ **Dependencies**:
- click (CLI interface)
- tomlkit (TOML generation)
- jsonschema (validation)
- rdflib-jsonld (JSON-LD processing)

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the MVP**:
   ```bash
   python test_mvp.py
   ```

3. **Use CLI**:
   ```bash
   python -m croissant_toml.cli to-toml sample.json -o sample.toml
   python -m croissant_toml.cli validate sample.toml
   python -m croissant_toml.cli to-json sample.toml -o roundtrip.json
   ```

4. **Use programmatically**:
   ```python
   from croissant_toml.converter import jsonld_to_toml, toml_to_jsonld
   jsonld_to_toml('input.json', 'output.toml')
   toml_to_jsonld('input.toml', 'output.json')
   ```

## Key Design Decisions

- **Minimal comments**: Clean, focused code for clarity
- **Extensible schema**: JSON Schema makes adding new Croissant fields straightforward
- **Human-readable TOML**: Comments and logical structure in generated TOML
- **Round-trip validation**: Ensures data integrity across conversions
- **Runnable out of the box**: Includes sample data and test script

## TOML Output Example

```toml
# Croissant Dataset Metadata
# Generated from JSON-LD format

[metadata]
# Dataset name
name = "Sample Dataset"
# Dataset description
description = "A sample dataset for testing Croissant TOML converter"
# Dataset version
version = "1.0.0"
# Dataset URL
url = "https://example.com/sample-dataset"
# Dataset license
license = "MIT"

[[record_sets]]
name = "examples"
description = "Example records with text and labels"

[[record_sets.field]]
name = "text"
description = "Input text content"
dataType = "sc:Text"

[[distributions]]
name = "data.csv"
description = "Main dataset file"
contentUrl = "https://example.com/data.csv"
encodingFormat = "text/csv"
```

This MVP provides a solid foundation for Croissant metadata conversion with clear extension points for additional fields and functionality.