# Development & Release Pipeline

## Quick Start for Contributors

### 1. Set Up Development Environment

```bash
# Clone the repository
git clone https://github.com/stuartp44/haduco.git
cd haduco

# Install development dependencies
pip install -r requirements_test.txt

# Run tests
pytest tests/

# Run linters
ruff check .
ruff format .
mypy custom_components/duco_ventilation_sun_control
```

### 2. Make Changes

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Example commits
git commit -m "feat: add new sensor type"
git commit -m "fix: resolve connection timeout"
git commit -m "docs: update installation guide"
```

See [Commit Guide](docs/COMMIT_GUIDE.md) for more examples.

### 3. Submit Pull Request

- Create a branch: `git checkout -b feat/my-feature`
- Push changes: `git push origin feat/my-feature`
- Open PR on GitHub
- All tests must pass before merge

## Automated Release Process

This project uses **semantic-release** for fully automated releases:

1. **Push to main** → Tests run automatically
2. **Commit analysis** → Determines version bump based on commit types
3. **Version update** → Updates `manifest.json` automatically
4. **Changelog** → Generates/updates `CHANGELOG.md`
5. **GitHub Release** → Creates release with notes
6. **Contributors** → Updates contributor list

### Version Bumping

| Commit Type | Example | Version Change |
|-------------|---------|----------------|
| `fix:` | `fix: sensor bug` | 1.2.0 → 1.2.1 (patch) |
| `feat:` | `feat: new sensor` | 1.2.0 → 1.3.0 (minor) |
| `feat!:` or `BREAKING CHANGE:` | `feat!: new config` | 1.2.0 → 2.0.0 (major) |

## Testing

### Run All Tests
```bash
pytest tests/ --cov=custom_components/duco_ventilation_sun_control --cov-report=term-missing
```

### Linting
```bash
# Check code
ruff check .

# Format code
ruff format .

# Type checking
mypy custom_components/duco_ventilation_sun_control
```

### HACS Validation
```bash
# Install HACS action locally (optional)
# Validates integration meets HACS requirements
```

## CI/CD Workflows

### Tests Workflow
- Runs on: Every push and PR
- Python versions: 3.11, 3.12
- Checks: pytest, ruff, mypy, HACS validation, hassfest

### Release Workflow
- Runs on: Push to main
- Actions: Semantic release, version bump, changelog, GitHub release

### Additional Workflows
- **PR Labeler**: Auto-labels PRs based on title
- **CodeQL**: Security scanning
- **Dependency Review**: Checks for vulnerable dependencies
- **Stale Issues**: Manages inactive issues/PRs

## Contributors

Contributors are automatically acknowledged! Check [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full list.

## Documentation

- [Release Pipeline Details](docs/RELEASE_PIPELINE.md)
- [Commit Message Guide](docs/COMMIT_GUIDE.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Best Practices

1. **Always use conventional commits** - Required for automatic releases
2. **Write tests** - Maintain or improve coverage
3. **Update docs** - Keep documentation current
4. **Small, focused commits** - Easier to review and track
5. **Run tests locally** - Before pushing changes

## Troubleshooting

### Tests Failing Locally

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Reinstall dependencies
pip install -r requirements_test.txt --force-reinstall

# Run with verbose output
pytest tests/ -v
```

### Linting Errors

```bash
# Auto-fix most issues
ruff check . --fix
ruff format .
```

### Release Not Triggering

- Ensure commits follow conventional format
- Check if `[skip ci]` is in commit message
- Verify tests passed on main branch

## Project Stats

![Tests](https://github.com/stuartp44/haduco/actions/workflows/tests.yml/badge.svg)
![Release](https://github.com/stuartp44/haduco/actions/workflows/release.yml/badge.svg)
[![codecov](https://codecov.io/gh/stuartp44/haduco/branch/main/graph/badge.svg)](https://codecov.io/gh/stuartp44/haduco)

---

**Need help?** Open an issue or check the [Contributing Guide](CONTRIBUTING.md)!
