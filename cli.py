import click
from pathlib import Path
from .converter import jsonld_to_toml, toml_to_jsonld
from .validator import validate_toml_file


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Croissant TOML Converter - Convert between JSON-LD and TOML formats."""
    pass


@main.command(name="to-toml")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output TOML file")
def to_toml(input_file, output):
    """Convert Croissant JSON-LD to TOML format."""
    if not output:
        output = input_file.with_suffix(".toml")

    try:
        jsonld_to_toml(input_file, output)
        click.echo(f"Successfully converted {input_file} to {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@main.command(name="to-json")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output JSON-LD file")
def to_json(input_file, output):
    """Convert TOML to Croissant JSON-LD format."""
    if not output:
        output = input_file.with_suffix(".json")

    try:
        toml_to_jsonld(input_file, output)
        click.echo(f"Successfully converted {input_file} to {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file):
    """Validate TOML file against Croissant schema."""
    try:
        is_valid, errors = validate_toml_file(input_file)
        if is_valid:
            click.echo(f"✓ {input_file} is valid")
        else:
            click.echo(f"✗ {input_file} is invalid:")
            for error in errors:
                click.echo(f"  - {error}")
            raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
