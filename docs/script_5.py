# Create converter.py
converter_content = '''import json
from typing import Dict, Any
from .parser import parse_jsonld_to_dict
from .generator import generate_toml_from_dict, dict_to_toml_string
from .validator import validate_dict_against_schema, toml_to_dict


def jsonld_to_toml(input_path: str, output_path: str):
    """Convert Croissant JSON-LD to TOML format."""
    # Parse JSON-LD
    normalized_data = parse_jsonld_to_dict(input_path)
    
    # Validate parsed data
    is_valid, errors = validate_dict_against_schema(normalized_data)
    if not is_valid:
        raise ValueError(f"Parsed data validation failed: {', '.join(errors)}")
    
    # Generate TOML
    generate_toml_from_dict(normalized_data, output_path)


def toml_to_jsonld(input_path: str, output_path: str):
    """Convert TOML to Croissant JSON-LD format."""
    # Load and validate TOML
    data = toml_to_dict(input_path)
    is_valid, errors = validate_dict_against_schema(data)
    if not is_valid:
        raise ValueError(f"TOML validation failed: {', '.join(errors)}")
    
    # Convert to JSON-LD structure
    jsonld_data = _dict_to_jsonld(data)
    
    # Write JSON-LD file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jsonld_data, f, indent=2, ensure_ascii=False)


def _dict_to_jsonld(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert normalized dictionary back to JSON-LD structure."""
    jsonld = {
        "@context": {
            "@vocab": "https://schema.org/",
            "cr": "https://mlcommons.org/croissant/",
            "data": {
                "@id": "cr:data",
                "@type": "@json"
            },
            "field": "cr:field",
            "filename": "cr:filename",
            "fileProperty": "cr:fileProperty",
            "format": "cr:format",
            "includes": "cr:includes",
            "isEnumeration": "cr:isEnumeration",
            "jsonPath": "cr:jsonPath",
            "recordSet": "cr:recordSet",
            "references": "cr:references",
            "regex": "cr:regex",
            "repeated": "cr:repeated",
            "replace": "cr:replace",
            "sc": "https://schema.org/",
            "separator": "cr:separator",
            "source": "cr:source",
            "subField": "cr:subField",
            "transform": "cr:transform"
        },
        "@type": "sc:Dataset"
    }
    
    # Map metadata back to JSON-LD structure
    if 'metadata' in data:
        metadata = data['metadata']
        
        # Map common fields back to schema.org terms
        field_mappings = {
            'name': 'name',
            'description': 'description',
            'version': 'version',
            'url': 'url',
            'license': 'license',
            'creator': 'creator',
            'date_created': 'dateCreated',
            'date_modified': 'dateModified'
        }
        
        for toml_key, jsonld_key in field_mappings.items():
            if toml_key in metadata:
                jsonld[jsonld_key] = metadata[toml_key]
        
        # Add remaining metadata fields
        for key, value in metadata.items():
            if key not in field_mappings:
                jsonld[key] = value
    
    # Map record sets
    if 'record_sets' in data and data['record_sets']:
        jsonld['cr:recordSet'] = data['record_sets']
    
    # Map distributions
    if 'distributions' in data and data['distributions']:
        jsonld['distribution'] = data['distributions']
    
    return jsonld


def validate_roundtrip(original_jsonld_path: str) -> bool:
    """Validate that JSON-LD -> TOML -> JSON-LD roundtrip preserves data."""
    try:
        # Load original
        with open(original_jsonld_path, 'r') as f:
            original = json.load(f)
        
        # Convert to TOML and back
        temp_toml = "/tmp/temp.toml"
        temp_jsonld = "/tmp/temp_roundtrip.json"
        
        jsonld_to_toml(original_jsonld_path, temp_toml)
        toml_to_jsonld(temp_toml, temp_jsonld)
        
        # Load roundtrip result
        with open(temp_jsonld, 'r') as f:
            roundtrip = json.load(f)
        
        # Basic comparison (could be enhanced)
        return _compare_jsonld_structure(original, roundtrip)
        
    except Exception:
        return False


def _compare_jsonld_structure(original: Dict, roundtrip: Dict) -> bool:
    """Compare JSON-LD structures for essential equality."""
    # Compare core fields
    core_fields = ['name', 'description', 'version', 'url']
    
    for field in core_fields:
        if original.get(field) != roundtrip.get(field):
            return False
    
    return True
'''

with open("croissant_toml/converter.py", "w") as f:
    f.write(converter_content)

print("Created croissant_toml/converter.py")