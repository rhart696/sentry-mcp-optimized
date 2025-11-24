# Contributing to Sentry MCP Optimized

First off, thank you for considering contributing to Sentry MCP Optimized! It's people like you that make this project a great tool for the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to rhart696@users.noreply.github.com.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Basic understanding of async Python
- Familiarity with Sentry API (helpful but not required)

### Your First Contribution

Unsure where to begin? You can start by looking through these issue labels:
- `good-first-issue` - Issues suitable for newcomers
- `help-wanted` - Issues where we need community help
- `documentation` - Documentation improvements
- `bug` - Bug fixes needed

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone git@github.com:YOUR_USERNAME/sentry-mcp-optimized.git
cd sentry-mcp-optimized

# Add upstream remote
git remote add upstream git@github.com:rhart696/sentry-mcp-optimized.git
```

### 2. Create Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if available)
pip install pre-commit
pre-commit install
```

### 4. Install MCP Optimizer Framework

```bash
# Clone and install the framework (if not already installed)
cd ..
git clone https://github.com/rhart696/mcp-optimizer-framework.git
cd mcp-optimizer-framework
pip install -e .
cd ../sentry-mcp-optimized
```

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Sentry credentials
# SENTRY_AUTH_TOKEN=your_token_here
# SENTRY_ORG_SLUG=your_org_here
```

### 6. Verify Setup

```bash
# Run tests to verify everything works
pytest tests/

# Run specific test file
pytest tests/test_sentry_adapter.py -v

# Check code formatting
black --check sentry_mcp/

# Run type checking
mypy sentry_mcp/
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (Python version, OS, etc.)
- **Code samples** or error messages
- **Screenshots** if applicable

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml).

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement needed?
- **Proposed solution** - how should it work?
- **Alternatives considered**
- **Additional context**

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml).

### Contributing Code

1. **Find or create an issue** describing what you want to work on
2. **Comment on the issue** to let others know you're working on it
3. **Create a branch** from `main` with a descriptive name
4. **Make your changes** following our code standards
5. **Write tests** for your changes
6. **Update documentation** as needed
7. **Submit a pull request**

## Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Formatter**: Black (run `black sentry_mcp/`)
- **Imports**: Sorted with `isort`
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all public APIs

### Code Organization

```python
# Good: Clear structure with type hints
async def list_issues(
    self,
    project: str,
    status: str = "unresolved",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    List issues for a project.

    Args:
        project: Project slug
        status: Issue status filter (default: "unresolved")
        limit: Maximum number of issues to return

    Returns:
        List of issue dictionaries

    Raises:
        ValueError: If project is empty
        aiohttp.ClientError: If API request fails
    """
    if not project:
        raise ValueError("Project slug is required")

    # Implementation here
    pass
```

### Naming Conventions

- **Functions/Methods**: `snake_case` (e.g., `list_issues`)
- **Classes**: `PascalCase` (e.g., `SentryAdaptor`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: Prefix with `_` (e.g., `_suggest_fix`)
- **Async functions**: Descriptive names indicating async nature

### Documentation Standards

- All public functions require docstrings
- Use Google-style docstrings
- Include examples for complex functions
- Update docs/ directory for major changes
- Keep README.md in sync with features

### Performance Considerations

This project is about optimization, so:

- **Minimize token usage** - return only necessary data
- **Use async/await** for all I/O operations
- **Batch operations** when possible
- **Cache aggressively** (with proper invalidation)
- **Profile before optimizing** - include benchmarks

### Security Practices

- **Never commit credentials** - use environment variables
- **Validate all inputs** from external sources
- **Sanitize data** before logging
- **Use prepared statements** or parameterized queries
- **Handle secrets securely** - no plaintext storage
- **Review dependencies** for vulnerabilities

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── test_sentry_adapter.py # Unit tests for adapter
├── test_operations.py     # Tests for operations
└── integration/
    └── test_live_sentry.py # Integration tests (requires credentials)
```

### Writing Tests

```python
import pytest
from sentry_mcp import SentryAdaptor

@pytest.mark.asyncio
async def test_list_issues_success(mock_sentry_api):
    """Test successful issue listing."""
    adaptor = SentryAdaptor(
        auth_token="test_token",
        org_slug="test_org"
    )

    issues = await adaptor.list_issues(project="test_project", limit=5)

    assert len(issues) == 5
    assert "id" in issues[0]
    assert "title" in issues[0]

@pytest.mark.asyncio
async def test_list_issues_with_empty_project(sentry_adaptor):
    """Test error handling for empty project."""
    with pytest.raises(ValueError, match="Project slug is required"):
        await sentry_adaptor.list_issues(project="")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sentry_mcp --cov-report=html

# Run specific test file
pytest tests/test_sentry_adapter.py

# Run tests matching pattern
pytest -k "test_list_issues"

# Run with verbose output
pytest -v

# Run only unit tests (skip integration)
pytest -m "not integration"

# Run only integration tests
pytest -m integration
```

### Test Coverage Requirements

- Minimum **80% code coverage** for new code
- All new features must include tests
- Bug fixes should include regression tests
- Integration tests for API interactions

### Mocking Guidelines

```python
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_sentry_api(mocker):
    """Mock Sentry API responses."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = [
        {"id": "1", "title": "Test Issue"}
    ]

    mocker.patch("aiohttp.ClientSession.get", return_value=mock_response)
    return mock_response
```

## Pull Request Process

### Before Submitting

1. **Update documentation** for any changed functionality
2. **Add tests** for new features or bug fixes
3. **Run the full test suite** and ensure all tests pass
4. **Run code formatters** (black, isort)
5. **Check type hints** with mypy
6. **Update CHANGELOG.md** with your changes
7. **Verify no merge conflicts** with main branch

### PR Title Format

Use conventional commit format:

- `feat: Add support for alert rules API`
- `fix: Handle rate limiting errors correctly`
- `docs: Update installation instructions`
- `test: Add integration tests for events`
- `refactor: Simplify error handling logic`
- `perf: Optimize token usage in list operations`

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed

## Performance Impact
- Token usage: [increased/decreased/no change]
- Latency: [faster/slower/no change]
- Benchmarks: [include if applicable]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated
- [ ] No new warnings or errors
```

### Review Process

1. **Automated checks** must pass (CI/CD, tests, linting)
2. **At least one maintainer approval** required
3. **Address review comments** promptly
4. **Squash commits** if requested
5. **Rebase on main** before merging

### After Merge

- Delete your feature branch
- Close related issues
- Update project board if applicable

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code review and contributions

### Getting Help

- Read the [documentation](docs/)
- Check [existing issues](https://github.com/rhart696/sentry-mcp-optimized/issues)
- Review [MCP Optimizer Framework docs](https://github.com/rhart696/mcp-optimizer-framework)
- Ask questions in GitHub Discussions

### Recognition

Contributors are recognized in:
- README.md Contributors section
- CHANGELOG.md for significant contributions
- GitHub contributors graph

## Development Tips

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use structlog for structured logging
logger = structlog.get_logger()
logger.debug("event_name", key="value", **context)
```

### Performance Profiling

```python
# Profile token usage
from mcp_optimizer_framework.metrics import TokenCounter

counter = TokenCounter()
result = await sentry.list_issues(project="test")
print(f"Tokens used: {counter.total_tokens}")
```

### Local Testing Against Real Sentry

```bash
# Set up test organization
export SENTRY_AUTH_TOKEN="your_test_token"
export SENTRY_ORG_SLUG="your_test_org"

# Run integration tests
pytest tests/integration/ -v
```

## License

By contributing to Sentry MCP Optimized, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask! We're here to help. Open an issue or reach out through GitHub Discussions.

Thank you for contributing to Sentry MCP Optimized!
