# Pull Request

## Description

Brief description of what this PR does.

Fixes #(issue number)

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Test updates

## Testing

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing locally

### Test Details
Describe the tests you ran and their results:

```bash
# Commands run
pytest tests/
```

## Performance Impact

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance regression (explain below)

**Token Usage**: [increased/decreased/no change]
**Latency**: [faster/slower/no change]
**Benchmarks** (if applicable):

```
Before: X ms, Y tokens
After:  X ms, Y tokens
```

## Documentation

- [ ] Code is self-documenting
- [ ] Docstrings added/updated
- [ ] README updated
- [ ] API documentation updated
- [ ] CHANGELOG updated
- [ ] ADR created (for significant decisions)

## Code Quality

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No new warnings or errors
- [ ] Type hints added where appropriate
- [ ] Error handling is appropriate

### Linting and Formatting
- [ ] `black sentry_mcp/` (code formatting)
- [ ] `mypy sentry_mcp/` (type checking)
- [ ] `pytest --cov=sentry_mcp` (test coverage >80%)

## Breaking Changes

Does this PR introduce breaking changes?

- [ ] No breaking changes
- [ ] Yes (describe below and update CHANGELOG)

**Breaking Changes Description**:
```
Describe what breaks and how users should update their code
```

## Checklist

- [ ] My code follows the project's coding style
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published
- [ ] I have updated the CHANGELOG.md
- [ ] I have checked my code and corrected any misspellings

## Screenshots (if applicable)

Add screenshots to help explain your changes.

## Additional Context

Add any other context about the pull request here.

## Reviewer Notes

Specific areas you'd like reviewers to focus on:

---

**By submitting this pull request, I confirm that my contribution is made under the terms of the MIT License.**
