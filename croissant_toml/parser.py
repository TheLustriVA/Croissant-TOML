import json
from typing import Dict, Any
from rdflib import Graph
from rdflib.plugin import register, Serializer
from rdflib.namespace import RDF, RDFS


def parse_jsonld_to_dict(jsonld_file_path: str) -> Dict[str, Any]:
    """Parse JSON-LD file and return normalized dictionary with flattened keys."""
    
    with open(jsonld_file_path, 'r', encoding='utf-8') as f:
        jsonld_data = json.load(f)
    
    # Create RDF graph and parse JSON-LD
    graph = Graph()
    graph.parse(data=json.dumps(jsonld_data), format='json-ld')
    
    # Extract normalized data structure
    normalized_data = {}
    
    # Handle basic metadata
    if isinstance(jsonld_data, dict):
        # Extract @context
        context = jsonld_data.get('@context', {})
        
        # Flatten and normalize keys
        flattened = _flatten_jsonld_keys(jsonld_data, context)
        normalized_data = _normalize_croissant_structure(flattened)
    
    return normalized_data


def _flatten_jsonld_keys(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten JSON-LD keys by removing prefixes and expanding contexts."""
    flattened = {}
    
    for key, value in data.items():
        if key.startswith('@'):
            continue
            
        # Remove common prefixes
        clean_key = key
        if ':' in key:
            clean_key = key.split(':', 1)[1]
        
        # Handle nested structures
        if isinstance(value, dict):
            flattened[clean_key] = _flatten_jsonld_keys(value, context)
        elif isinstance(value, list):
            flattened[clean_key] = [
                _flatten_jsonld_keys(item, context) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            flattened[clean_key] = value
    
    return flattened


def _normalize_croissant_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Croissant-specific structure for TOML conversion."""
    normalized = {
        'metadata': {},
        'record_sets': [],
        'distributions': []
    }
    
    # Map common Croissant fields
    field_mappings = {
        'name': 'metadata.name',
        'description': 'metadata.description',
        'version': 'metadata.version',
        'url': 'metadata.url',
        'license': 'metadata.license',
        'creator': 'metadata.creator',
        'dateCreated': 'metadata.date_created',
        'dateModified': 'metadata.date_modified',
        'recordSet': 'record_sets',
        'distribution': 'distributions'
    }
    
    for key, value in data.items():
        if key in field_mappings:
            target_path = field_mappings[key]
            _set_nested_value(normalized, target_path, value)
        else:
            # Handle unknown fields in metadata section
            normalized['metadata'][key] = value
    
    return normalized


def _set_nested_value(data: Dict[str, Any], path: str, value: Any):
    """Set value at nested path in dictionary."""
    parts = path.split('.')
    current = data
    
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = value
