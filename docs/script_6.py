# Create schema.json
schema_content = '''{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "title": "Croissant TOML Schema",
  "description": "JSON Schema for validating Croissant dataset metadata in TOML format",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "description": "Core dataset metadata",
      "properties": {
        "name": {
          "type": "string",
          "description": "Dataset name"
        },
        "description": {
          "type": "string",
          "description": "Dataset description"
        },
        "version": {
          "type": "string",
          "description": "Dataset version"
        },
        "url": {
          "type": "string",
          "format": "uri",
          "description": "Dataset URL"
        },
        "license": {
          "type": "string",
          "description": "Dataset license"
        },
        "creator": {
          "oneOf": [
            {"type": "string"},
            {
              "type": "object",
              "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "url": {"type": "string"}
              }
            }
          ],
          "description": "Dataset creator"
        },
        "date_created": {
          "type": "string",
          "format": "date",
          "description": "Creation date"
        },
        "date_modified": {
          "type": "string",
          "format": "date",
          "description": "Last modification date"
        }
      },
      "required": ["name", "description"],
      "additionalProperties": true
    },
    "record_sets": {
      "type": "array",
      "description": "Dataset record sets",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "field": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "dataType": {"type": "string"},
                "source": {"type": "string"}
              },
              "required": ["name"]
            }
          }
        },
        "required": ["name"],
        "additionalProperties": true
      }
    },
    "distributions": {
      "type": "array",
      "description": "Dataset distributions/files",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "contentUrl": {"type": "string"},
          "encodingFormat": {"type": "string"},
          "sha256": {"type": "string"}
        },
        "required": ["contentUrl"],
        "additionalProperties": true
      }
    }
  },
  "required": ["metadata"],
  "additionalProperties": false
}'''

with open("croissant_toml/schema.json", "w") as f:
    f.write(schema_content)

print("Created croissant_toml/schema.json")