import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
import tomlkit
from jsonschema import validate, ValidationError


def validate_toml_file(toml_file_path: str) -> Tuple[bool, List[str]]:
    """Validate TOML file against Croissant schema."""
    try:
        # Load TOML file
        with open(toml_file_path, 'r', encoding='utf-8') as f:
            toml_content = f.read()

        # Parse TOML to dictionary
        data = tomlkit.loads(toml_content)
        dict_data = _tomlkit_to_dict(data)

        # Validate against schema
        return validate_dict_against_schema(dict_data)

    except Exception as e:
        return False, [f"Failed to load TOML file: {str(e)}"]


def validate_dict_against_schema(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate dictionary against JSON schema."""
    try:
        # Load schema
        schema_path = Path(__file__).parent / 'schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Validate
        validate(instance=data, schema=schema)
        return True, []

    except ValidationError as e:
        return False, [f"Validation error: {e.message}"]
    except FileNotFoundError:
        return False, ["Schema file not found"]
    except Exception as e:
        return False, [f"Validation failed: {str(e)}"]


def _tomlkit_to_dict(data) -> Dict[str, Any]:
    """Convert tomlkit objects to plain dictionary."""
    if isinstance(data, dict):
        return {key: _tomlkit_to_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_tomlkit_to_dict(item) for item in data]
    else:
        # Handle tomlkit specific types
        if hasattr(data, 'value'):
            return data.value
        return data


def toml_to_dict(toml_file_path: str) -> Dict[str, Any]:
    """Load TOML file and convert to dictionary."""
    with open(toml_file_path, 'r', encoding='utf-8') as f:
        toml_content = f.read()

    data = tomlkit.loads(toml_content)
    return _tomlkit_to_dict(data)
