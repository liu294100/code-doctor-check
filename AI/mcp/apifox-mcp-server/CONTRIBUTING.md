# Contributing to Apifox MCP Server

Thank you for your interest in contributing to Apifox MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you are expected to uphold our code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- A clear description of the feature
- Why this feature would be useful
- Possible implementation approach (if you have one)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure nothing is broken
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Keep changes focused - one feature/fix per PR

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js (for CLI MCP testing)
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/apifox-mcp-server.git
cd apifox-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apifox_cli_mcp --cov=apifox_api_mcp

# Run specific test file
pytest tests/test_cli_mcp.py
```

### Code Style

We use:
- [Black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [flake8](https://flake8.pycqa.org/) for linting
- [mypy](https://mypy.readthedocs.io/) for type checking

```bash
# Format code
black .
isort .

# Check linting
flake8
mypy apifox_cli_mcp apifox_api_mcp
```

## Project Structure

```
apifox-mcp-server/
├── apifox_cli_mcp/         # CLI-based MCP server
│   ├── __init__.py
│   └── server.py
├── apifox_api_mcp/         # API-based MCP server
│   ├── __init__.py
│   └── server.py
├── tests/                  # Test files
├── docs/                   # Documentation
├── .github/                # GitHub templates and workflows
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── pyproject.toml          # Project configuration
├── README.md               # English documentation
├── README_CN.md            # Chinese documentation
├── CONTRIBUTING.md         # This file
├── CHANGELOG.md            # Version history
└── LICENSE                 # MIT License
```

## Documentation

- Keep README.md and README_CN.md in sync
- Document new tools with clear descriptions and examples
- Update CHANGELOG.md for notable changes

## Release Process

Releases are managed by maintainers. Version numbers follow [Semantic Versioning](https://semver.org/):

- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

## Questions?

Feel free to open an issue with the "question" label if you have any questions about contributing.

Thank you for contributing! 🎉
