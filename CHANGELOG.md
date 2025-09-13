# Changelog

All notable changes to the Croissant-TOML project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced validation for RAI (Responsible AI) fields with controlled vocabularies
- Support for RAI section in TOML format following specification
- Enhanced URL/IRI validation using RFC 3986 standards
- ISO 8601 date format validation
- SHA256 hash format validation
- Support for `conformsTo` field in metadata (required by specification)
- Support for `changeLog` field in metadata for version management
- Inline comments in generated TOML files based on field descriptions
- Namespace handling for schema.org fields under `[metadata.schema]`
- Preservation of camelCase for schema.org properties
- Support for both `recordsets` and `record_sets` naming conventions
- Support for both `distribution` and `distributions` naming conventions

### Changed
- **BREAKING**: Updated parser to use `recordsets` instead of `record_sets` to match specification
- **BREAKING**: Updated parser to use `distribution` (singular, array of tables) instead of `distributions`
- Enhanced validator with additional validation checks beyond basic JSON schema
- Generator now follows specification structure with proper section naming
- Parser now preserves camelCase for schema.org fields while normalizing internal fields
- Improved error messages for validation failures

### Fixed
- Corrected TOML Array of Tables syntax for recordsets and distributions
- Fixed handling of nested RAI annotation and demographics sections
- Improved field ordering in generated TOML files for better readability

### Documentation
- Updated README with specification-compliant examples
- Added comprehensive contributing guidelines
- Added code of conduct for academic collaboration
- Added changelog for version tracking

## [0.1.0] - 2024-12-09

### Added
- Initial implementation of JSON-LD to TOML conversion
- Basic TOML to JSON-LD conversion
- CLI interface for conversions and validation
- Basic schema validation
- Support for core Croissant metadata fields
- Package structure and basic documentation

### Known Issues
- Limited RAI field support
- Basic validation only
- No controlled vocabulary validation
- Snake_case naming convention differs from specification
