# Makefile for Croissant-TOML development

.PHONY: help install test lint format clean docs build release

# Default target
help:
	@echo "Available targets:"
	@echo "  install     Install dependencies and package in development mode"
	@echo "  test        Run all tests with coverage"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  clean       Clean up temporary files and cache"
	@echo "  docs        Generate documentation"
	@echo "  build       Build package for distribution"
	@echo "  release     Build and upload to PyPI"
	@echo "  pre-commit  Install and run pre-commit hooks"

# Development setup
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
	pip install pytest pytest-cov black flake8 mypy isort pre-commit bandit safety

# Testing
test:
	pytest tests/ --cov=croissant_toml --cov-report=term-missing --cov-report=html

test-integration:
	python -m croissant_toml.cli to-toml sample.json -o test_output.toml
	python -m croissant_toml.cli validate test_output.toml
	python -m croissant_toml.cli to-json test_output.toml -o roundtrip.json
	@echo "Integration tests completed successfully"

# Code quality
lint:
	flake8 croissant_toml tests
	mypy croissant_toml --ignore-missing-imports
	bandit -r croissant_toml/
	safety check

format:
	black croissant_toml tests
	isort croissant_toml tests

# Pre-commit hooks
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -f test_output.toml roundtrip.json

# Documentation
docs:
	@echo "Documentation generation would go here"
	@echo "Consider using Sphinx or mkdocs for academic documentation"

# Build and release
build: clean
	python -m build

release: build
	python -m twine upload dist/*

# Development workflow
dev-setup: install pre-commit
	@echo "Development environment setup complete"

# Run all quality checks
check: lint test
	@echo "All quality checks passed"
