# Display final project structure
import os

def display_tree(path, prefix="", max_depth=3, current_depth=0):
    """Display directory tree structure."""
    if current_depth >= max_depth:
        return
    
    items = []
    if os.path.isdir(path):
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return
    
    for i, item in enumerate(items):
        if item.startswith('.'):
            continue
            
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item}")
        
        if os.path.isdir(item_path) and current_depth < max_depth - 1:
            next_prefix = prefix + ("    " if is_last else "│   ")
            display_tree(item_path, next_prefix, max_depth, current_depth + 1)

print("Croissant TOML Converter MVP - Project Structure")
print("=" * 50)
print()
print(".")
display_tree(".", max_depth=2)

print("\nFiles created:")
print("-" * 20)

files = [
    "croissant_toml/__init__.py",
    "croissant_toml/cli.py",
    "croissant_toml/parser.py", 
    "croissant_toml/generator.py",
    "croissant_toml/validator.py",
    "croissant_toml/converter.py",
    "croissant_toml/schema.json",
    "croissant_toml/README.md",
    "requirements.txt",
    "setup.py",
    "sample.json",
    "test_mvp.py"
]

for file in files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"✓ {file} ({size} bytes)")
    else:
        print(f"✗ {file} (missing)")

print(f"\nTotal files created: {len([f for f in files if os.path.exists(f)])}")

# Create a quick installation guide
install_guide = """

QUICK START GUIDE
=================

1. Install dependencies:
   pip install -r requirements.txt

2. Install package (optional):
   pip install -e .

3. Test the MVP:
   python test_mvp.py

4. Use CLI commands:
   python -m croissant_toml.cli to-toml sample.json -o sample.toml
   python -m croissant_toml.cli validate sample.toml
   python -m croissant_toml.cli to-json sample.toml -o roundtrip.json

5. Use programmatically:
   from croissant_toml.converter import jsonld_to_toml
   jsonld_to_toml('input.json', 'output.toml')
"""

print(install_guide)