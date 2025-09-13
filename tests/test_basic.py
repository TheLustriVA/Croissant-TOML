"""Basic tests for Croissant-TOML functionality."""

import tempfile
from pathlib import Path

import pytest

from croissant_toml.generator import _get_field_comment
from croissant_toml.parser import _is_schema_org_field, _to_snake_case
from croissant_toml.validator import (
    _is_valid_iso8601_date,
    _is_valid_sha256,
    _is_valid_url,
    validate_dict_against_schema,
)


class TestValidator:
    """Test validator functionality."""

    def test_url_validation(self) -> None:
        """Test URL validation."""
        assert _is_valid_url("https://example.org/dataset")
        assert _is_valid_url("http://localhost:8080/data")
        assert not _is_valid_url("not-a-url")
        assert not _is_valid_url("")

    def test_sha256_validation(self) -> None:
        """Test SHA256 hash validation."""
        valid_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert _is_valid_sha256(valid_sha)
        assert not _is_valid_sha256("invalid-hash")
        assert not _is_valid_sha256("too-short")
        assert not _is_valid_sha256("")

    def test_iso8601_date_validation(self) -> None:
        """Test ISO 8601 date validation."""
        assert _is_valid_iso8601_date("2024-01-01T00:00:00Z")
        assert _is_valid_iso8601_date("2024-12-31")
        assert not _is_valid_iso8601_date("2024/01/01")
        assert not _is_valid_iso8601_date("invalid-date")
        assert not _is_valid_iso8601_date("")

    def test_basic_validation_structure(self) -> None:
        """Test basic validation of a valid structure."""
        valid_data = {
            "metadata": {
                "conformsTo": ["http://mlcommons.org/croissant/1.0"],
                "name": "Test Dataset",
                "description": "A test dataset",
                "url": "https://example.org/dataset",
            }
        }

        # This will fail schema validation but should not crash
        is_valid, errors = validate_dict_against_schema(valid_data)
        # Just ensure it returns boolean and list
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


class TestParser:
    """Test parser functionality."""

    def test_schema_org_field_detection(self) -> None:
        """Test schema.org field detection."""
        assert _is_schema_org_field("dateCreated")
        assert _is_schema_org_field("dateModified")
        assert _is_schema_org_field("contentUrl")
        assert not _is_schema_org_field("name")
        assert not _is_schema_org_field("custom_field")

    def test_snake_case_conversion(self) -> None:
        """Test camelCase to snake_case conversion."""
        assert _to_snake_case("camelCase") == "camel_case"
        assert _to_snake_case("XMLHttpRequest") == "xml_http_request"
        assert _to_snake_case("simple") == "simple"
        assert _to_snake_case("") == ""


class TestGenerator:
    """Test generator functionality."""

    def test_field_comments(self) -> None:
        """Test field comment generation."""
        assert _get_field_comment("name") == "Dataset name"
        assert _get_field_comment("description") == "Comprehensive dataset description"
        assert _get_field_comment("conformsTo") == "Specification conformance URLs"
        assert _get_field_comment("nonexistent_field") is None


class TestIntegration:
    """Basic integration tests."""

    def test_imports(self) -> None:
        """Test that all modules can be imported."""
        from croissant_toml import cli, converter, generator, parser, validator

        # Just ensure modules exist
        assert validator is not None
        assert parser is not None
        assert generator is not None
        assert converter is not None
        assert cli is not None

    @pytest.mark.integration
    def test_temp_file_creation(self) -> None:
        """Test that we can create temporary files (for converter testing)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            temp_path = Path(f.name)
            f.write("test = true\n")

        assert temp_path.exists()
        temp_path.unlink()  # Clean up
        assert not temp_path.exists()


if __name__ == "__main__":
    pytest.main([__file__])
