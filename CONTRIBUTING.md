# Contributing to Croissant-TOML

Thank you for your interest in contributing to the Croissant-TOML project! This document provides guidelines for contributing to this academic software project.

## Code of Conduct

This project adheres to a code of conduct that promotes inclusive and respectful collaboration. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- familiarity with TOML format and JSON-LD
- Understanding of machine learning metadata standards (helpful but not required)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/Croissant-TOML.git
   cd Croissant-TOML
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

5. Run tests to ensure everything is working:
   ```bash
   python -m pytest tests/
   ```

## Contributing Process

### 1. Create an Issue

Before making changes, please create an issue to discuss:
- Bug reports
- Feature requests
- Documentation improvements
- Questions about the specification

### 2. Create a Branch

Create a descriptive branch name:
```bash
git checkout -b feature/add-validation-for-rai-fields
git checkout -b fix/parser-camelcase-handling
git checkout -b docs/update-installation-guide
```

### 3. Make Changes

- Write clean, readable code following Python PEP 8 standards
- Add appropriate type hints
- Include docstrings for new functions and classes
- Update relevant documentation
- Add or update tests for new functionality

### 4. Testing

Ensure all tests pass:
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=croissant_toml

# Test specific functionality
python -m croissant_toml.cli validate sample.toml
python -m croissant_toml.cli to-toml sample.json
```

### 5. Documentation

Update documentation as needed:
- Update README.md for new features
- Add docstrings to new functions
- Update examples if CLI interface changes
- Update specification compliance notes

### 6. Submit Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin your-branch-name
   ```

2. Create a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Examples of new functionality
   - Notes about specification compliance

## Code Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write comprehensive docstrings
- Keep functions focused and modular
- Use meaningful variable and function names

### Testing

- Write unit tests for new functions
- Test both success and error cases
- Include integration tests for CLI functionality
- Test specification compliance
- Aim for high test coverage

### Documentation

- Update docstrings for any modified functions
- Include examples in docstrings where helpful
- Update README.md for user-facing changes
- Document any specification deviations or extensions

## Specification Compliance

This project implements the "Human-Readable TOML Specification for Croissant and Croissant-RAI Metadata." When contributing:

- Ensure changes maintain semantic equivalence with Croissant/Croissant-RAI
- Follow the specification's design principles
- Test against official Croissant examples where possible
- Document any extensions or deviations

## Areas for Contribution

### High Priority
- Enhanced validation for RAI fields
- Better error messages and debugging
- Performance optimizations
- Additional test cases

### Medium Priority
- Support for additional Croissant extensions
- Improved CLI interface
- Better handling of complex JSON-LD structures
- Documentation website

### Research Contributions
- Evaluation against other metadata formats
- Usability studies with domain scientists
- Integration with ML workflow tools
- Performance benchmarking

## Questions and Support

- Create an issue for questions about the code
- Email the maintainers for academic collaboration inquiries
- Check existing issues before creating new ones
- Join discussions in existing issues and pull requests

## Academic Collaboration

This is an academic project, and we welcome:
- Collaboration on research papers
- Integration with other academic tools
- Evaluation and feedback studies
- Extensions for domain-specific needs

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (CC0-1.0).

## Acknowledgments

Contributors will be acknowledged in:
- Repository contributors list
- Academic publications where appropriate
- Project documentation
- Future presentations about the work

Thank you for contributing to making ML metadata more accessible and human-readable!
