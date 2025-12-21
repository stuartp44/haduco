# Contributing to DUCO Ventilation & Sun Control

Thank you for your interest in contributing! 

## About This Project

This project was originally created by [@Sikerdebaard](https://github.com/Sikerdebaard). We welcome contributions from everyone to help improve and expand this Home Assistant integration.

## How to Contribute

### Reporting Bugs

- Use the bug report template when creating an issue
- Include as much detail as possible
- Provide steps to reproduce the issue
- Include relevant logs and configuration

### Suggesting Features

- Use the feature request template
- Explain the problem you're trying to solve
- Describe your proposed solution
- Consider alternative approaches

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow conventional commits** format for commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions or changes
   - `refactor:` for code refactoring
   - `perf:` for performance improvements
   - `chore:` for maintenance tasks
   - `ci:` for CI/CD changes

3. **Write tests** for your changes when applicable
4. **Ensure all tests pass**:
   ```bash
   pytest tests/
   ```

5. **Lint your code**:
   ```bash
   ruff check .
   ruff format .
   mypy custom_components/duco_ventilation_sun_control
   ```

6. **Update documentation** if needed
7. **Submit your pull request** using the PR template

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```
<type>: <description>

[optional body]

[optional footer]
```

### Examples

```
feat: add support for new sensor type
fix: resolve issue with sensor state updates
docs: update README with installation instructions
test: add unit tests for coordinator
refactor: simplify configuration flow logic
```

### Breaking Changes

For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:

```
feat!: change configuration schema
```

or

```
feat: change configuration schema

BREAKING CHANGE: Configuration format has changed. Users need to update their config.
```

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/stuartp44/haduco.git
   cd haduco
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements_test.txt
   ```

3. **Run tests**:
   ```bash
   pytest tests/
   ```

4. **Run linters**:
   ```bash
   ruff check .
   ruff format .
   mypy custom_components/duco_ventilation_sun_control
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for classes and functions
- Keep lines under 120 characters
- Use meaningful variable and function names

## Testing

- Write unit tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use pytest fixtures for common test setup

## Documentation

- Update README.md if adding new features
- Document configuration options
- Include code examples where helpful
- Keep documentation clear and concise

## Questions?

Feel free to open an issue for questions or discussion!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
