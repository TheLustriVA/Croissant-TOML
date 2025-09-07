# Create requirements.txt
requirements_content = '''click>=8.0.0
tomlkit>=0.11.0
jsonschema>=4.0.0
rdflib-jsonld>=0.6.0
rdflib>=6.0.0
'''

with open("requirements.txt", "w") as f:
    f.write(requirements_content)

print("Created requirements.txt")