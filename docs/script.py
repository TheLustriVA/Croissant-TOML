import os

# Create the project directory structure
os.makedirs("croissant_toml", exist_ok=True)

# Create __init__.py
init_content = '''"""
Croissant TOML Converter - Convert between Croissant JSON-LD and human-readable TOML.
"""

__version__ = "0.1.0"
'''

with open("croissant_toml/__init__.py", "w") as f:
    f.write(init_content)

print("Created croissant_toml/__init__.py")