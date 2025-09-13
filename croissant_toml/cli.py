"""
Croissant TOML Command-Line Interface.

Provides click-based CLI commands for converting Croissant metadata between
JSON-LD and TOML formats, as well as for schema validation. Entry point for
batch and interactive workflows involving metadata conversion and compliance
checks for MLCommons Croissant projects.
"""

from pathlib import Path
from typing import Optional

import click

from .converter import jsonld_to_toml, toml_to_jsonld
from .validator import validate_toml_file


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Croissant TOML Converter - Convert between JSON-LD and TOML formats."""
    pass


@main.command(name="to-toml")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output", type=click.Path(path_type=Path), help="Output TOML file"
)
def to_toml(input_file: Path, output: Optional[Path]) -> None:
    """Convert Croissant JSON-LD to TOML format."""
    if not output:
        output = input_file.with_suffix(".toml")

    try:
        jsonld_to_toml(str(input_file), str(output))
        click.echo(f"Successfully converted {input_file} to {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command(name="to-json")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output", type=click.Path(path_type=Path), help="Output JSON-LD file"
)
def to_json(input_file: Path, output: Optional[Path]) -> None:
    """Convert TOML to Croissant JSON-LD format."""
    if not output:
        output = input_file.with_suffix(".json")

    try:
        toml_to_jsonld(str(input_file), str(output))
        click.echo(f"Successfully converted {input_file} to {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate TOML file against Croissant schema."""
    try:
        is_valid, errors = validate_toml_file(str(input_file))

        if is_valid:
            click.echo(f"✓ {input_file} is valid")
        else:
            click.echo(f"✗ {input_file} is invalid: ")
            for error in errors:
                click.echo(f" - {error}")
            raise click.Abort()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e


if __name__ == "__main__":
    main()
