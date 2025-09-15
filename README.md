# Croissant-TOML: Human-Readable ML Dataset Metadata

[![CI](https://github.com/TheLustriVA/Croissant-TOML/actions/workflows/ci.yml/badge.svg)](https://github.com/TheLustriVA/Croissant-TOML/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

A Python tool for converting between [Croissant/Croissant-RAI](https://github.com/mlcommons/croissant) JSON-LD metadata and human-readable TOML format, implementing the [Human-Readable TOML Specification for Croissant and Croissant-RAI Metadata](https://arxiv.org/abs/XXXX.XXXXX).

## Overview

This library provides bidirectional conversion between Croissant dataset metadata formats:

- **JSON-LD**: Machine-readable format following schema.org vocabulary and Croissant specifications
- **TOML**: Human-readable configuration format with comments, logical structure, and enhanced accessibility

## Rationale

TOML provides a far more accessible and genuinely open way of handling ML metadata than JSON-LD because of its human readability. The effort put into acknowledging bias, potential harm, and the unintentional reinforcement of existing power structures in modern ML metadata seems, to me, utterly wasted if that very documentation can't be easily read by non-technical people.

This project implements an academically rigorous specification that maintains complete semantic equivalence with Croissant and Croissant-RAI while dramatically improving human comprehension and authoring experience.

## Features

- ✅ **Bidirectional conversion**: JSON-LD ↔ TOML with semantic preservation
- ✅ **Complete RAI support**: Full Responsible AI metadata section handling
- ✅ **Enhanced validation**: URL/IRI validation, date formats, controlled vocabularies
- ✅ **Human-centered design**: Inline comments, logical organization, field descriptions
- ✅ **Specification compliance**: Implements the complete TOML specification for Croissant
- ✅ **Schema.org compatibility**: Preserves camelCase and proper namespace handling
- ✅ **Academic rigor**: Designed for research reproducibility and documentation

## Installation

```bash
pip install -r requirements.txt
pip install -e .  # Install in development mode
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

## TOML Format Specification

The TOML format follows the [Human-Readable TOML Specification for Croissant and Croissant-RAI Metadata](https://arxiv.org/abs/XXXX.XXXXX) and organizes metadata into logical sections:

### Basic Structure

```toml
# Croissant Dataset Metadata
# Generated from JSON-LD format
# Conforms to: http://mlcommons.org/croissant/1.0

[metadata]
# Required: Specification conformance
conformsTo = [
  "http://mlcommons.org/croissant/1.0",
  "http://mlcommons.org/croissant/RAI/1.0"
]
# Dataset name
name = "COVID-19 Medical Imaging Dataset"
# Comprehensive dataset description
description = "Chest X-ray images for COVID-19 detection research"
# Dataset version (semantic versioning recommended)
version = "2.1.0"
# Dataset homepage URL
url = "https://example.org/covid-dataset"
# License URL or identifier
license = "https://creativecommons.org/licenses/by/4.0/"
# Publication date in ISO 8601 format
datePublished = 2024-03-15T10:30:00Z

# Schema.org fields grouped separately
[metadata.schema]
creator = "Medical Research Institute"
keywords = ["medical imaging", "covid-19", "chest x-ray"]

# File distributions as Array of Tables
[[distribution]]
type = "FileObject"
id = "training_images"
name = "Training Image Set"
contentUrl = "https://example.org/train.zip"
encodingFormat = "application/zip"
sha256 = "abc123def456..."

# Recordsets with nested field definitions
[recordsets.training_data]
type = "RecordSet"
id = "training_records"
key = ["image_id"]

[[recordsets.training_data.fields]]
id = "image_id"
name = "Image Identifier"
dataType = "Text"
description = "Unique identifier for each image"

[recordsets.training_data.fields.source]
fileObject = "metadata.csv"
extract.column = "id"

# Responsible AI metadata
[rai]
# Description of data collection process
dataCollection = "Images sourced from public repositories with proper attribution and consent verification"
dataCollectionType = ["Web Scraping", "API Collection", "Manual Curation"]
# Known biases in the dataset
dataBiases = [
  "Geographic bias toward Western countries",
  "Temporal bias toward recent years (2020-2024)"
]
# Intended use cases for the dataset
dataUseCases = ["Training", "Validation", "Research Use Only"]

[rai.annotation]
annotationPlatform = "Custom web interface"
annotationsPerItem = 3
totalAnnotators = 25

[rai.annotation.demographics]
gender = { male = 12, female = 11, nonbinary = 2 }
age_ranges = { "18-30" = 10, "31-45" = 12, "46-65" = 3 }
```

### Key Specification Features

1. **Human Readability**: Inline comments explaining each field's purpose
2. **Logical Organization**: Related fields grouped in intuitive sections
3. **Namespace Handling**: Schema.org fields properly nested under `[metadata.schema]`
4. **RAI Integration**: Complete Responsible AI metadata support with controlled vocabularies
5. **Validation**: Enhanced validation for URLs, dates, checksums, and enumerations
6. **Semantic Fidelity**: Perfect preservation of Croissant/Croissant-RAI semantics

## Programmatic Usage

### Basic Conversion

```python
from croissant_toml.converter import jsonld_to_toml, toml_to_jsonld

# JSON-LD to TOML
jsonld_to_toml('input.json', 'output.toml')

# TOML to JSON-LD
toml_to_jsonld('input.toml', 'output.json')
```

### Enhanced Validation

```python
from croissant_toml.validator import validate_toml_file

is_valid, errors = validate_toml_file('dataset.toml')
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

### Custom Processing with RAI Support

```python
from croissant_toml.parser import parse_jsonld_to_dict
from croissant_toml.generator import generate_toml_from_dict

# Parse JSON-LD to normalized dict
data = parse_jsonld_to_dict('input.json')

# Add RAI metadata
data['rai'] = {
    'dataCollection': 'Collected via automated web scraping',
    'dataBiases': ['Geographic bias toward English-speaking countries'],
    'dataUseCases': ['Research Use Only']
}

# Generate TOML with RAI support
generate_toml_from_dict(data, 'output.toml')
```

## Specification Compliance

This implementation follows the complete [Human-Readable TOML Specification for Croissant and Croissant-RAI Metadata](https://arxiv.org/abs/XXXX.XXXXX), ensuring:

- **Semantic Fidelity**: Perfect preservation of Croissant/Croissant-RAI semantics
- **Human-Centered Design**: Optimization for human readability and comprehension
- **Validation Compatibility**: Integration with existing Croissant validation ecosystems
- **Academic Defensibility**: All design decisions grounded in established research
- **Extensibility**: Support for future Croissant extensions and domain-specific needs

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for details.

### Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Install pre-commit hooks: `pre-commit install`
5. Run tests: `pytest tests/`

### Areas for Contribution

- Enhanced validation for domain-specific extensions
- Performance optimizations for large datasets
- Integration with ML workflow tools
- Usability studies with domain scientists
- Additional controlled vocabularies for RAI fields

## Academic Use

This project supports academic research and welcomes:

- Collaboration on research papers
- Integration with other academic tools
- Evaluation and feedback studies
- Extensions for domain-specific needs

### Citation

If you use this software in your research, please cite:

```bibtex
@software{bicheno2024croissant_toml,
  title = {Croissant-TOML: A Human-Readable TOML Specification for ML Dataset Metadata},
  author = {Bicheno, Kieran},
  year = {2024},
  url = {https://github.com/TheLustriVA/Croissant-TOML}
}
```

## Project Structure

```bash
croissant_toml/
├── __init__.py           # Package initialization
├── cli.py                # Command-line interface
├── parser.py             # JSON-LD parsing with RAI support
├── generator.py          # TOML generation with enhanced formatting
├── validator.py          # Enhanced validation with controlled vocabularies
├── converter.py          # High-level conversion orchestration
├── schema.json           # JSON Schema for TOML validation
└── README.md             # Documentation
```

## License

This project is released under the CC0-1.0 License, dedicating it to the public domain to maximize accessibility and reuse in academic and research contexts.

## Acknowledgments

- MLCommons Croissant Working Group for the original specification
- Tom Preston-Werner for the TOML format specification
- The research community working on ethical AI and responsible dataset documentation
- All contributors to open science and reproducible research practices

---

*For more of my work on ethical AI and documentation, see: [The Pile Datasheet](https://huggingface.co/datasets/EleutherAI/pile)*
